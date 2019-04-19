""" STOMP consumer that listens to BZ and reproduces to Fedora Messaging.

Authors:    Ralph Bean <rbean@redhat.com>

"""

import datetime
import logging
import time

import pytz


LOGGER = logging.getLogger(__name__)


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
