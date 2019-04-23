import datetime
import logging

import pytz
from fedora_messaging.api import Message, publish
from fedora_messaging.exceptions import PublishReturned, ConnectionException

from .utils import convert_datetimes


LOGGER = logging.getLogger(__name__)

# These are bug fields we're going to try and pass on to fedora-messaging.
BUG_FIELDS = [
    "alias",
    "assigned_to",
    # 'attachments',  # These can contain binary things we don't want to send.
    "blocks",
    "cc",
    "classification",
    "component",
    "components",
    "creation_time",
    "depends_on",
    "description",
    "docs_contact",
    "estimated_time",
    "external_bugs",
    "fixed_in",
    "flags",
    "groups",
    "id",
    "is_cc_accessible",
    "is_confirmed",
    "is_creator_accessible",
    "is_open",
    "keywords",
    "last_change_time",
    "operating_system",
    "platform",
    "priority",
    "product",
    "qa_contact",
    "actual_time",
    "remaining_time",
    "reporter",
    "resolution",
    "see_also",
    "severity",
    "status",
    "summary",
    "target_milestone",
    "target_release",
    "url",
    "version",
    "versions",
    "weburl",
    "whiteboard",
]


class MessageRelay:
    def __init__(self, config):
        self.config = config
        self._allowed_products = self.config.get("bugzilla", {}).get("products", [])

    def on_stomp_message(self, body, headers):

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
        obj = headers['destination'].split('bugzilla.')[1].split('.')[0]
        if obj not in body:
            LOGGER.debug("DROP: message has no object field. Non public.")
            return
        objdict = {}
        bug = None
        if obj == 'bug':
            # just take the bug dict, converting datetimes
            bug = convert_datetimes(body['bug'])
        else:
            # unpick the bug dict from the object dict
            bug = convert_datetimes(body[obj].pop('bug'))
            objdict[obj] = convert_datetimes(body[obj])

        # As of https://bugzilla.redhat.com/show_bug.cgi?id=1248259, bugzilla
        # will send the product along with the initial message, so let's check
        # it.
        product_name = bug["product"]["name"]
        if product_name not in self._allowed_products:
            LOGGER.debug("DROP: %r not in %r" % (product_name, self._allowed_products))
            return

        LOGGER.debug("Organizing metadata for #%s" % bug["id"])
        bug = dict([(attr, bug.get(attr, None)) for attr in BUG_FIELDS])

        body["timestamp"] = datetime.datetime.fromtimestamp(
            int(headers["timestamp"]) / 1000.0, pytz.UTC
        )
        event = body.get("event")
        event = convert_datetimes(event)

        # backwards compat for bz5
        if bug["assigned_to"]:
            bug["assigned_to"] = bug["assigned_to"]["login"]
        if bug["component"]:
            bug["component"] = bug["component"]["name"]
        bug["cc"] = bug["cc"] or []
        if bug["reporter"]:
            bug["creator"] = bug["reporter"]["login"]
        if bug["operating_system"]:
            bug["op_sys"] = bug["operating_system"]
        event["who"] = event["user"]["login"]
        event["changes"] = event.get("changes", [])
        for change in event["changes"]:
            change["field_name"] = change["field"]
        if obj == 'comment':
            # I would expect this to be real_name so we're not spaffing
            # email addresses all over, but I checked and historically
            # it was definitely login
            objdict[obj]['author'] = event.get('user', {}).get('login', '')
        # end backwards compat handling

        topic = "bug.update"
        if 'bug.create' in headers['destination']:
            topic = "bug.new"

        # construct message dict, add the object dict we got earlier
        # (for non-'bug' object messages)
        body = dict(
            bug=bug,
            event=event,
            headers=headers,
        )
        body.update(objdict)

        LOGGER.debug("Republishing #%s" % bug['id'])
        try:
            message = Message(
                topic="bugzilla.{}".format(topic),
                body=body,
            )
            publish(message)
        except PublishReturned as e:
            LOGGER.warning("Fedora Messaging broker rejected message {}: {}".format(message.id, e))
        except ConnectionException as e:
            LOGGER.warning("Error sending message {}: {}".format(message.id, e))
