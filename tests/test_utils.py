"""Tests for bugzilla2fedmsg.utils.

Authors:    Aurélien Bompard <abompard@fedoraproject.org>

"""

import pytest
import requests.exceptions
from fasjson_client.errors import APIError

from bugzilla2fedmsg.utils import cache, email_to_fas


@pytest.fixture
def real_cache():
    cache.configure(
        backend="dogpile.cache.memory", expiration_time=60, replace_existing_backend=True
    )
    yield
    cache.configure(backend="dogpile.cache.null", replace_existing_backend=True)


def test_email_to_fas_fpo(fakefasjson):
    username = email_to_fas("dummy@fedoraproject.org", fakefasjson)
    assert username == "dummy"
    fakefasjson.search.assert_not_called()


@pytest.mark.parametrize(
    "exception",
    [
        APIError("Dummy error", 500),
        requests.exceptions.ConnectionError("Dummy error"),
        requests.exceptions.ReadTimeout("Dummy error"),
    ],
)
def test_email_to_fas_error(fakefasjson, caplog, real_cache, exception):
    fakefasjson.search.side_effect = exception
    username = email_to_fas("dgunchev@gmail.com", fakefasjson)
    assert username is None
    fakefasjson.search.assert_called_once_with(rhbzemail="dgunchev@gmail.com")
    assert "Could not look up the FAS user with rhbzemail = dgunchev@gmail.com" in caplog.text


def test_email_to_fas_error_not_cached(fakefasjson, real_cache):
    """A failed lookup must not be cached as if the user did not exist."""
    search = fakefasjson.search.side_effect
    fakefasjson.search.side_effect = requests.exceptions.ConnectionError("Dummy error")
    assert email_to_fas("dgunchev@gmail.com", fakefasjson) is None
    fakefasjson.search.side_effect = search
    assert email_to_fas("dgunchev@gmail.com", fakefasjson) == "dgunchev"
