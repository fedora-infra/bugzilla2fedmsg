"""Tests for bugzilla2fedmsg.relay.

Authors:    Adam Williamson <awilliam@redhat.com>

"""

import logging

import fedora_messaging.exceptions
import pytest

import bugzilla2fedmsg.relay
import bugzilla2fedmsg.utils


@pytest.fixture
def test_config(fakefasjson):
    return {
        "fasjson_url": "https://fasjson.example.com",
        "bugzilla": {"products": ["Fedora", "Fedora EPEL"]},
        "cache": {"backend": "dogpile.cache.null"},
    }


@pytest.fixture
def testrelay(fakefasjson, test_config):
    return bugzilla2fedmsg.relay.MessageRelay(test_config)


@pytest.fixture
def real_cache(test_config):
    bugzilla2fedmsg.utils.cache.configure(
        backend="dogpile.cache.memory", expiration_time=60, replace_existing_backend=True
    )
    yield
    bugzilla2fedmsg.utils.cache.configure(**test_config["cache"], replace_existing_backend=True)


def test_bug_create(testrelay, fakepublish, fakefasjson, bug_create_message):
    """Check correct result for bug.create message."""
    testrelay.on_kafka_message(bug_create_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.topic == "bugzilla.bug.new"
    assert "product" in message.body["bug"]
    assert message.body["event"]["routing_key"] == "bug.create"
    # this tests convert_datetimes
    createtime = message.body["bug"]["creation_time"]
    assert createtime == 1770218051.0
    assert message.body["agent_name"] == "dgunchev"
    assert message.body["usernames"] == ["dgunchev", "lv"]


def test_bug_modify(testrelay, fakepublish, bug_modify_message):
    """Check correct result for bug.modify message."""
    testrelay.on_kafka_message(bug_modify_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.topic == "bugzilla.bug.update"
    assert "product" in message.body["bug"]
    assert message.body["event"]["routing_key"] == "bug.modify"
    assert message.body["agent_name"] is None
    assert message.body["usernames"] == ["adamw", "davide", "upstream-release-monitoring"]


def test_comment_create(testrelay, fakepublish, comment_create_message):
    """Check correct result for comment.create message."""
    testrelay.on_kafka_message(comment_create_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.topic == "bugzilla.bug.update"
    assert message.body["comment"]["author"] == "rjones@redhat.com"
    assert message.body["comment"]["creation_time"] == 1770217973.0
    assert message.body["comment"]["number"] == 1
    assert message.body["comment"]["id"] == 2436732
    assert message.body["comment"]["is_private"] is False
    assert message.body["comment"]["body"].startswith("Unclear, does it work outside a container")

    # we probably don't need to check these whole things...
    assert "product" in message.body["bug"]
    assert message.body["event"]["routing_key"] == "comment.create"
    assert message.body["agent_name"] == "rjones"
    assert message.body["usernames"] == ["adamw", "rjones"]


def test_attachment_create(testrelay, fakepublish, attachment_create_message):
    """Check correct result for attachment.create message."""
    testrelay.on_kafka_message(attachment_create_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.topic == "bugzilla.bug.update"
    assert message.body["attachment"] == {
        "description": "File: proc_pid_status",
        "file_name": "proc_pid_status",
        "is_patch": False,
        "creation_time": 1770218054.0,
        "id": 2128166,
        "flags": [],
        "last_change_time": 1770218054.0,
        "content_type": "text/plain",
        "is_obsolete": False,
        "is_private": False,
    }
    # we probably don't need to check these whole things...
    assert "product" in message.body["bug"]
    assert message.body["event"]["routing_key"] == "attachment.create"
    assert message.body["agent_name"] == "peter"
    assert message.body["usernames"] == ["davide", "peter"]


def test_attachment_modify(testrelay, fakepublish, attachment_modify_message):
    """Check correct result for attachment.modify message."""
    testrelay.on_kafka_message(attachment_modify_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.topic == "bugzilla.bug.update"
    assert message.body["attachment"] == {
        "description": "File: maps",
        "file_name": "maps",
        "is_patch": False,
        "creation_time": 1770218056.0,
        "id": 2128167,
        "flags": [],
        "last_change_time": 1770218056.0,
        "content_type": "text/plain",
        "is_obsolete": False,
        "is_private": False,
    }
    # we probably don't need to check these whole things...
    assert "product" in message.body["bug"]
    assert message.body["event"]["routing_key"] == "attachment.modify"
    assert message.body["agent_name"] == "joe"
    assert message.body["usernames"] == ["davide", "joe"]


def test_private_drop(testrelay, fakepublish, private_message):
    """Check that we drop (don't publish) a private message."""
    testrelay.on_kafka_message(private_message)
    assert fakepublish.call_count == 0


def test_other_product_drop(testrelay, fakepublish, other_product_message):
    """Check that we drop (don't publish) a message for a product
    we don't want to cover. As our fake hub doesn't really have a
    config, the products we care about are the defaults: 'Fedora'
    and 'Fedora EPEL'.
    """
    testrelay.on_kafka_message(other_product_message)
    assert fakepublish.call_count == 0


def test_bz4_compat(
    testrelay, test_config, fakefasjson, fakepublish, bug_create_message, comment_create_message
):
    """This tests various modifications we make to the bug dict in
    the name of 'backwards compatibility', i.e. making messages
    look more like they did before Bugzilla 5.
    """
    test_config["bugzilla"]["bz4compat"] = True
    bz4relay = bugzilla2fedmsg.relay.MessageRelay(test_config)
    bz4relay.on_kafka_message(bug_create_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.body["bug"]["assigned_to"] == "lvrabec@redhat.com"
    assert message.body["bug"]["component"] == "smplayer"
    assert message.body["bug"]["product"] == "Fedora"
    assert message.body["bug"]["cc"] == []
    assert message.body["bug"]["creator"] == "dgunchev@gmail.com"
    assert message.body["bug"]["op_sys"] == "Unspecified"
    assert message.body["event"]["who"] == "dgunchev@gmail.com"
    assert message.body["bug"]["weburl"] == "https://bugzilla.redhat.com/show_bug.cgi?id=2436734"
    # we need a comment message to test this
    fakepublish.reset_mock()
    testrelay.on_kafka_message(comment_create_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.body["comment"]["author"] == "rjones@redhat.com"


def test_bz4_compat_disabled(
    test_config, fakefasjson, fakepublish, bug_create_message, comment_create_message
):
    """Test that we *don't* make Bugzilla 4 compat modifications
    if the option is switched off. Tests only the destructive ones
    as they're the ones we really want to avoid, and if these
    aren't happening it's pretty certain the others aren't either.
    """
    test_config["bugzilla"]["bz4compat"] = False
    nobz4relay = bugzilla2fedmsg.relay.MessageRelay(test_config)
    nobz4relay.on_kafka_message(bug_create_message)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert all(item in message.body["bug"]["assigned_to"] for item in ("login", "id", "real_name"))
    assert all(item in message.body["bug"]["component"] for item in ("id", "name"))
    assert all(item in message.body["bug"]["product"] for item in ("id", "name"))


def test_publish_exception_publishreturned(testrelay, fakepublish, bug_create_message, caplog):
    """Check that we handle PublishReturned exception from publish
    correctly.
    """
    fakepublish.side_effect = fedora_messaging.exceptions.PublishReturned("oops!")
    # this should not raise any exception
    testrelay.on_kafka_message(bug_create_message)
    assert fakepublish.call_count == 1
    # check the logging worked
    assert "Fedora Messaging broker rejected message" in caplog.text


def test_publish_exception_connectionexception(testrelay, fakepublish, bug_create_message, caplog):
    """Check that we handle ConnectionException from publish
    correctly.
    """
    # First test PublishReturned
    fakepublish.side_effect = fedora_messaging.exceptions.ConnectionException("oops!")
    # this should not raise any exception
    testrelay.on_kafka_message(bug_create_message)
    assert fakepublish.call_count == 1
    # check the logging worked
    assert "Error sending message" in caplog.text


def test_needinfo_removed(testrelay, fakepublish, bug_modify_message_four_changes):
    bug_modify_message_four_changes["event"]["changes"][2] = {
        "field": "cc",
        "removed": "",
        "added": "awilliam@redhat.com",
    }
    bug_modify_message_four_changes["event"]["changes"][3]["added"] = ""
    testrelay.on_kafka_message(bug_modify_message_four_changes)
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    assert message.body["agent_name"] is None
    assert message.body["usernames"] == ["adamw", "davide"]


def test_needinfo_bad(testrelay, fakepublish, bug_modify_message_four_changes):
    last_change = bug_modify_message_four_changes["event"]["changes"][3]
    last_change["added"] = "some garbage"
    try:
        testrelay.on_kafka_message(bug_modify_message_four_changes)
    except IndexError as e:
        pytest.fail(str(e))
    assert fakepublish.call_count == 1


def test_cached_fasjson(
    test_config,
    testrelay,
    real_cache,
    fakefasjson,
    fakepublish,
    bug_create_message,
    comment_create_message,
    caplog,
):
    caplog.set_level(logging.DEBUG, "bugzilla2fedmsg.utils")
    testrelay.on_kafka_message(bug_create_message)
    assert fakefasjson.search.call_count == 2
    assert len([msg for msg in caplog.messages if msg.startswith("Searching FASJSON with")]) == 2
    caplog.clear()
    fakefasjson.search.reset_mock()
    testrelay.on_kafka_message(bug_create_message)
    assert fakefasjson.search.call_count == 0
    # No "searching" log messages
    assert len([msg for msg in caplog.messages if msg.startswith("Searching FASJSON with")]) == 0
