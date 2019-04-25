import datetime
import logging

import pytz
from fedora_messaging.api import publish
from fedora_messaging.exceptions import PublishReturned, ConnectionException
from fedora_messaging.message import INFO

from bugzilla2fedmsg_schema.schema import MessageV1, MessageV1BZ4

from .utils import convert_datetimes


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
        bug["weburl"] = "https://bugzilla.redhat.com/show_bug.cgi?id=%s" % bug['id']
    event["who"] = event["user"]["login"]
    event["changes"] = event.get("changes", [])
    for change in event["changes"]:
        change["field_name"] = change["field"]
    if obj == 'comment':
        # I would expect this to be real_name so we're not spaffing
        # email addresses all over, but I checked and historically
        # it was definitely login
        objdict[obj]['author'] = event.get('user', {}).get('login', '')


class MessageRelay:
    def __init__(self, config):
        self.config = config
        self._allowed_products = self.config.get("bugzilla", {}).get("products", [])
        self._bz4_compat_mode = self.config.get("bugzilla", {}).get("bz4compat", True)

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

        body["timestamp"] = datetime.datetime.fromtimestamp(
            int(headers["timestamp"]) / 1000.0, pytz.UTC
        )
        event = body.get("event")
        event = convert_datetimes(event)

        if self._bz4_compat_mode:
            _bz4_compat_transform(bug, event, objdict, obj)

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
        messageclass = MessageV1
        if self._bz4_compat_mode:
            messageclass = MessageV1BZ4
        try:
            message = messageclass(
                topic="bugzilla.{}".format(topic),
                body=body,
                severity=INFO,
            )
            publish(message)
        except PublishReturned as e:
            LOGGER.warning("Fedora Messaging broker rejected message {}: {}".format(message.id, e))
        except ConnectionException as e:
            LOGGER.warning("Error sending message {}: {}".format(message.id, e))
