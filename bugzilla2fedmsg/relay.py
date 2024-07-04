import datetime
import logging

import pytz
from bugzilla2fedmsg_schema import MessageV1, MessageV1BZ4
from fasjson_client import Client as FasjsonClient
from fedora_messaging.api import publish
from fedora_messaging.exceptions import ConnectionException, PublishReturned
from fedora_messaging.message import INFO

from .utils import convert_datetimes, email_to_fas, needinfo_email


LOGGER = logging.getLogger(__name__)


def _bz4_compat_transform(bug, event, objdict, obj):
    """Modify the bug, event and obj dicts for a message to look more
    like a Bugzilla 4-era message's dicts did. Returns nothing as it
    modifies the dicts in place.
    """
    if bug.get("assigned_to", {}).get("login"):
        bug["assigned_to"] = bug["assigned_to"]["login"]
    if bug.get("component", {}).get("name"):
        bug["component"] = bug["component"]["name"]
    if bug.get("product", {}).get("name"):
        bug["product"] = bug["product"]["name"]
    bug["cc"] = bug.get("cc", [])
    if bug.get("reporter", {}).get("login"):
        bug["creator"] = bug["reporter"]["login"]
    if bug.get("operating_system"):
        bug["op_sys"] = bug["operating_system"]
    if not bug.get("weburl"):
        bug["weburl"] = f"https://bugzilla.redhat.com/show_bug.cgi?id={bug['id']}"
    event["who"] = event["user"]["login"]
    event["changes"] = event.get("changes", [])
    for change in event["changes"]:
        change["field_name"] = change["field"]
    if obj == "comment":
        # I would expect this to be real_name so we're not spaffing
        # email addresses all over, but I checked and historically
        # it was definitely login
        objdict[obj]["author"] = event.get("user", {}).get("login", "")


class DropMessage(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MessageRelay:
    def __init__(self, config):
        self.config = config
        self._allowed_products = self.config.get("bugzilla", {}).get("products", [])
        self._bz4_compat_mode = self.config.get("bugzilla", {}).get("bz4compat", True)
        self._fasjson = FasjsonClient(self.config["fasjson_url"])

    def on_stomp_message(self, body, headers):
        try:
            message_body = self._get_message_body(body, headers)
        except DropMessage as e:
            LOGGER.debug(f"DROP: {e}")
            return

        topic = "bug.update"
        if "bug.create" in headers["destination"]:
            topic = "bug.new"

        LOGGER.debug("Republishing #%s", message_body["bug"]["id"])
        messageclass = MessageV1
        if self._bz4_compat_mode:
            messageclass = MessageV1BZ4
        try:
            message = messageclass(
                topic=f"bugzilla.{topic}",
                body=message_body,
                severity=INFO,
            )
            publish(message)
        except PublishReturned as e:
            LOGGER.warning(f"Fedora Messaging broker rejected message {message.id}: {e}")
        except ConnectionException as e:
            LOGGER.warning(f"Error sending message {message.id}: {e}")

    def _get_message_body(self, body, headers):
        # in BZ 5.0+, public messages include a key for the 'object',
        # whatever the object is. So 'bug.*' messages have a 'bug'
        # dict...but 'comment.*' messages have a 'comment' dict,
        # 'attachment.*' messages have an 'attachment' dict and so on.
        # For all non-'bug' objects, this dict has the bug dict within
        # it. See:
        # https://bugzilla.redhat.com/docs/en/html/integrating/api/Bugzilla/Extension/Push.html
        # destination looks something like
        # "/topic/VirtualTopic.eng.bugzilla.bug.modify"
        # this splits out the 'bug' part
        obj = headers["destination"].split("bugzilla.")[1].split(".")[0]
        if obj not in body:
            raise DropMessage("message has no object field. Non public.")
        objdict = {}
        bug = None
        if obj == "bug":
            # just take the bug dict, converting datetimes
            bug = convert_datetimes(body["bug"])
        else:
            # unpick the bug dict from the object dict
            bug = convert_datetimes(body[obj].pop("bug"))
            objdict[obj] = convert_datetimes(body[obj])

        # As of https://bugzilla.redhat.com/show_bug.cgi?id=1248259, bugzilla
        # will send the product along with the initial message, so let's check
        # it.
        product_name = bug["product"]["name"]
        if product_name not in self._allowed_products:
            raise DropMessage(f"{product_name!r} not in {self._allowed_products}")

        body["timestamp"] = datetime.datetime.fromtimestamp(
            int(headers["timestamp"]) / 1000.0, pytz.UTC
        )
        event = body.get("event")
        event = convert_datetimes(event)

        if self._bz4_compat_mode:
            _bz4_compat_transform(bug, event, objdict, obj)

        # construct message dict, add the object dict we got earlier
        # (for non-'bug' object messages)
        body = dict(bug=bug, event=event, headers=headers)
        body.update(objdict)

        # user from the event dict: person who triggered the event
        agent_name = email_to_fas(event["user"]["login"], self._fasjson)
        body["agent_name"] = agent_name

        # usernames: all FAS usernames affected by the action
        all_emails = self._get_all_emails(body)
        usernames = set()
        for email in all_emails:
            username = email_to_fas(email, self._fasjson)
            if username is None:
                continue
            usernames.add(username)
        if agent_name is not None:
            usernames.add(agent_name)
        usernames = list(usernames)
        usernames.sort()
        body["usernames"] = usernames

        return body

    def _get_all_emails(self, body):
        """List of email addresses of all users relevant to the action
        that generated this message.
        """
        emails = set()

        # bug reporter and assignee
        emails.add(body["bug"]["reporter"]["login"])
        if self._bz4_compat_mode:
            emails.add(body["bug"]["assigned_to"])
        else:
            emails.add(body["bug"]["assigned_to"]["login"])

        for change in body["event"].get("changes", []):
            if change["field"] == "cc":
                # anyone added to CC list
                for email in change["added"].split(","):
                    email.strip()
                    if email:
                        emails.add(email)
            elif change["field"] == "flag.needinfo":
                # anyone for whom a 'needinfo' flag is set
                email = needinfo_email(change["added"])
                if email:
                    emails.add(email)

        # Strip anything that made it in erroneously
        for email in list(emails):
            if email.endswith("lists.fedoraproject.org"):
                emails.remove(email)

        emails = list(emails)
        return emails
