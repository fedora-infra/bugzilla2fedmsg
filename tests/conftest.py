"""Test fixtures for bugzilla2fedmsg.relay.

Authors:    Adam Williamson <awilliam@redhat.com>

"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest


@pytest.fixture
def fakepublish():
    with mock.patch("bugzilla2fedmsg.relay.publish", autospec=True) as _mock:
        yield _mock


FASJSON_USER_MAP = {
    "dgunchev@gmail.com": "dgunchev",
    "lvrabec@redhat.com": "lv",
    "awilliam@redhat.com": "adamw",
    "peter@sonniger-tag.eu": "peter",
    "joequant@gmail.com": "joe",
    "rjones@redhat.com": "rjones",
    "davide@cavalca.name": "davide",
}


@pytest.fixture
def fakefasjson():
    client = mock.Mock(name="fasjson")

    def _search(rhbzemail):
        try:
            return SimpleNamespace(result=[{"username": FASJSON_USER_MAP[rhbzemail]}])
        except KeyError:
            return SimpleNamespace(result=[])

    client.search.side_effect = _search
    with mock.patch("bugzilla2fedmsg.relay.FasjsonClient", return_value=client):
        yield client


FIXTURES_DIR = Path(__file__).parent.joinpath("fixtures")


@pytest.fixture(scope="function")
def bug_create_message(request):
    """Sample upstream bug.create message."""
    with open(FIXTURES_DIR.joinpath("bug-create-1.json")) as fh:
        return json.loads(fh.read())


@pytest.fixture(scope="function")
def bug_modify_message(request):
    """Sample upstream bug.modify message."""
    with open(FIXTURES_DIR.joinpath("bug-modify-1.json")) as fh:
        return json.loads(fh.read())


@pytest.fixture(scope="function")
def bug_modify_message_four_changes(request):
    """Sample upstream bug.modify message with four changes."""
    with open(FIXTURES_DIR.joinpath("bug-modify-2.json")) as fh:
        return json.loads(fh.read())


@pytest.fixture(scope="function")
def comment_create_message(request):
    """Sample upstream comment.create message."""
    with open(FIXTURES_DIR.joinpath("comment-create-1.json")) as fh:
        return json.loads(fh.read())


@pytest.fixture(scope="function")
def attachment_create_message(request):
    """Sample upstream attachment.create message."""
    with open(FIXTURES_DIR.joinpath("attachment-create-1.json")) as fh:
        return json.loads(fh.read())


@pytest.fixture(scope="function")
def attachment_modify_message(request):
    """Sample upstream attachment.modify message."""
    with open(FIXTURES_DIR.joinpath("attachment-modify-1.json")) as fh:
        return json.loads(fh.read())


@pytest.fixture(scope="function")
def private_message(request):
    """Sample upstream private message."""
    with open(FIXTURES_DIR.joinpath("private-1.json")) as fh:
        return json.loads(fh.read())


@pytest.fixture(scope="function")
def other_product_message(request):
    """Sample upstream message for another product."""
    with open(FIXTURES_DIR.joinpath("other-product-1.json")) as fh:
        return json.loads(fh.read())
