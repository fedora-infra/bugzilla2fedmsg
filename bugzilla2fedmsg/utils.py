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
