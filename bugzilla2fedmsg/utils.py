""" STOMP consumer that listens to BZ and reproduces to Fedora Messaging.

Authors:    Ralph Bean <rbean@redhat.com>

"""

import datetime
import logging

import pytz


LOGGER = logging.getLogger(__name__)


def convert_datetimes(obj):
    """Recursively convert the ISO-8601ish date/time strings we get
    from stomp to epoch integers (because this is what fedmsg used to
    emit when we sent it datetime instances).
    """

    if isinstance(obj, list):
        return [convert_datetimes(item) for item in obj]
    elif isinstance(obj, dict):
        return dict([(k, convert_datetimes(v)) for k, v in obj.items()])
    else:
        try:
            # the string we get is YYYY-MM-DDTHH:MM:SS, no timezone,
            # no microseconds. The previous code (for handling results
            # from querying Bugzilla directly) assumed this was a UTC
            # date, and from comparing some test messages to the web
            # UI it does indeed seem to be.
            ourdate = datetime.datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S")
            ourdate = ourdate.replace(tzinfo=pytz.UTC)
            return ourdate.timestamp()
        except (ValueError, TypeError):
            return obj


def email_to_fas(email, fasjson):
    """Try to get a FAS username from an email address, return None if no FAS username is found"""
    if email.endswith("@fedoraproject.org"):
        return email.rsplit("@", 1)[0]
    LOGGER.debug("Looking for a FAS user with rhbzemail = %s", email)
    results = fasjson.search(rhbzemail=email).result
    if len(results) == 1:
        LOGGER.debug("Found %s", results[0]["username"])
        return results[0]["username"]
    LOGGER.debug("No match")
    return None
