import datetime
import logging

import pytz
from fedora_messaging.api import Message, publish
from fedora_messaging.exceptions import PublishReturned, ConnectionException

from .utils import convert_datetimes, find_relevant_item


LOGGER = logging.getLogger(__name__)

# These are bug fields we're going to try and pass on to fedora-messaging.
BUG_FIELDS = [
    "alias",
    "assigned_to",
    # 'attachments',  # These can contain binary things we don't want to send.
    "blocks",
    "cc",
    "classification",
    "comments",
    "component",
    "components",
    "creation_time",
    "creator",
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
    "op_sys",
    "platform",
    "priority",
    "product",
    "qa_contact",
    "actual_time",
    "remaining_time",
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

        if "bug" not in body:
            LOGGER.debug("DROP: message has no 'bug' field. Non public.")
            return

        # As of https://bugzilla.redhat.com/show_bug.cgi?id=1248259, bugzilla
        # will send the product along with the initial message, so let's check
        # it.
        product_name = body["bug"]["product"]["name"]
        if product_name not in self._allowed_products:
            LOGGER.debug("DROP: %r not in %r" % (product_name, self._allowed_products))
            return

        LOGGER.debug("Organizing metadata for #%s" % body["bug"]["id"])
        bug = dict([(attr, body["bug"].get(attr, None)) for attr in BUG_FIELDS])
        bug = convert_datetimes(bug)

        body["timestamp"] = datetime.datetime.fromtimestamp(
            int(headers["timestamp"]) / 1000.0, pytz.UTC
        )
        comment = find_relevant_item(body, bug["comments"], "time")
        event = body.get("event")
        event = convert_datetimes(event)

        # backwards compat for bz5
        if bug["assigned_to"]:
            bug["assigned_to"] = bug["assigned_to"]["login"]
        if bug["component"]:
            bug["component"] = bug["component"]["name"]
        bug["cc"] = bug["cc"] or []
        event["who"] = event["user"]["login"]
        event["changes"] = event.get("changes", [])
        for change in event["changes"]:
            change["field_name"] = change["field"]
        # end backwards compat handling

        # If there are no events in the history, then this is a new bug.
        topic = "bug.update"
        if not event and len(bug["comments"]) == 1:
            topic = "bug.new"

        LOGGER.debug("Republishing #%s" % body["bug"]["id"])
        try:
            message = Message(
                topic="bugzilla.{}".format(topic),
                body=dict(bug=bug, event=event, comment=comment, headers=headers),
            )
            publish(message)
        except PublishReturned as e:
            LOGGER.warning("Fedora Messaging broker rejected message {}: {}".format(message.id, e))
        except ConnectionException as e:
            LOGGER.warning("Error sending message {}: {}".format(message.id, e))
