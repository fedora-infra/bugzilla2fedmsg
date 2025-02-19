"""Tests for bugzilla2fedmsg.utils.

Authors:    Aurélien Bompard <abompard@fedoraproject.org>

"""

import pytest

from bugzilla2fedmsg.utils import email_to_fas


def test_email_to_fas_fpo(fakefasjson):
    username = email_to_fas("dummy@fedoraproject.org", fakefasjson)
    assert username == "dummy"
    fakefasjson.search.assert_not_called()


@pytest.mark.parametrize("exception_class", [ConnectionError, TimeoutError])
def test_email_to_fas_error(fakefasjson, caplog, exception_class):
    fakefasjson.search.side_effect = exception_class("Dummy error")
    username = email_to_fas("dgunchev@gmail.com", fakefasjson)
    assert username is None
    fakefasjson.search.assert_called_once_with(rhbzemail="dgunchev@gmail.com")
    assert "Could not find a FAS user with rhzemail = dgunchev@gmail.com" in caplog.text
