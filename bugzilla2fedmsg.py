# -*- coding: utf-8 -*-
""" Moksha consumer that listens to BZ over STOMP and reproduces to fedmsg.

Authors:    Ralph Bean <rbean@redhat.com>

"""

import datetime
import pytz
import socket
import time

import fedmsg
import fedmsg.config
import fedmsg.meta
import moksha.hub.api
import moksha.hub.reactor

# These are bug fields we're going to try and pass on to fedmsg.
bug_fields = [
    'alias',
    'assigned_to',
    # 'attachments',  # These can contain binary things we don't want to send.
    'blocks',
    'cc',
    'classification',
    'comments',
    'component',
    'components',
    'creation_time',
    'creator',
    'depends_on',
    'description',
    'docs_contact',
    'estimated_time',
    'external_bugs',
    'fixed_in',
    'flags',
    'groups',
    'id',
    'is_cc_accessible',
    'is_confirmed',
    'is_creator_accessible',
    'is_open',
    'keywords',
    'last_change_time',
    'op_sys',
    'platform',
    'priority',
    'product',
    'qa_contact',
    'actual_time',
    'remaining_time',
    'resolution',
    'see_also',
    'severity',
    'status',
    'summary',
    'target_milestone',
    'target_release',
    'url',
    'version',
    'versions',
    'weburl',
    'whiteboard',
]


def convert_datetimes(obj):
    """ Recursively convert bugzilla DateTimes to stdlib datetimes. """

    if isinstance(obj, list):
        return [convert_datetimes(item) for item in obj]
    elif isinstance(obj, dict):
        return dict([
            (k, convert_datetimes(v))
            for k, v in obj.items()
        ])
    elif hasattr(obj, 'timetuple'):
        timestamp = time.mktime(obj.timetuple())
        return datetime.datetime.fromtimestamp(timestamp, pytz.UTC)
    else:
        return obj


class BugzillaConsumer(moksha.hub.api.Consumer):

    def __init__(self, hub):
        self.config = config = hub.config
        self.topic = config['stomp_queue']

        super(BugzillaConsumer, self).__init__(hub)

        # Backwards compat.  We used to have a self.debug...
        self.debug = self.log.info

        products = config.get('bugzilla.products', 'Fedora, Fedora EPEL')
        self.products = [product.strip() for product in products.split(',')]

        # First, initialize fedmsg and bugzilla in this thread's context.
        hostname = socket.gethostname().split('.', 1)[0]
        fedmsg.init(name='bugzilla2fedmsg.%s' % hostname)

        self.debug("Initialized bz2fm STOMP consumer.")

    def consume(self, msg):
        topic, msg, headers = msg['topic'], msg['body'], msg['headers']

        if 'bug' not in msg:
            self.debug("DROP: message has no 'bug' field. Non public.")
            return

        # As of https://bugzilla.redhat.com/show_bug.cgi?id=1248259, bugzilla
        # will send the product along with the initial message, so let's check
        # it.
        if msg['bug']['product']['name'] not in self.products:
            self.debug("DROP: %r not in %r" % (
                msg['bug']['product']['name'], self.products))
            return

        self.debug("Organizing metadata for #%s" % msg['bug']['id'])
        bug = msg['bug']
        bug = dict([(attr, bug.get(attr, None)) for attr in bug_fields])
        bug = convert_datetimes(bug)

        msg['timestamp'] = datetime.datetime.fromtimestamp(
            int(headers['timestamp']) / 1000.0, pytz.UTC)
        comment = self.find_relevant_item(msg, bug['comments'], 'time')
        event = msg.get('event')
        event = convert_datetimes(event)

        # backwards compat for fedmsg.meta for bz5
        if bug['assigned_to']:
            bug['assigned_to'] = bug['assigned_to']['login']
        if bug['component']:
            bug['component'] = bug['component']['name']
        bug['cc'] = bug['cc'] or []
        event['who'] = event['user']['login']
        event['changes'] = event.get('changes', [])
        for change in event['changes']:
            change['field_name'] = change['field']
        # end backwards compat handling

        # If there are no events in the history, then this is a new bug.
        topic = 'bug.update'
        if not event and len(bug['comments']) == 1:
            topic = 'bug.new'

        self.debug("Republishing #%s" % msg['bug']['id'])
        fedmsg.publish(
            modname='bugzilla',
            topic=topic,
            msg=dict(
                bug=bug,
                event=event,
                comment=comment,
                headers=headers,
            ),
        )

    @staticmethod
    def find_relevant_item(msg, history, key):
        """ Find the change from the BZ history with the closest timestamp to a
        given message.  Unfortunately, we can't rely on matching the timestamps
        exactly so instead we say that if the best match is within 60s of the
        message, then return it.  Otherwise return None.
        """

        if not history:
            return None

        best = history[0]
        best_delta = abs(best[key] - msg['timestamp'])

        for event in history[1:]:
            if abs(event[key] - msg['timestamp']) < best_delta:
                best = event
                best_delta = abs(best[key] - msg['timestamp'])

        if best_delta < datetime.timedelta(seconds=60):
            return best
        else:
            return None
