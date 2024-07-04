""" Tests for bugzilla2fedmsg_schemas.

We are basically going to use the relays to construct messages
just as we do in test_relay, then check the messages validate
and test the various schema methods. We parametrize the tests
to test all the schema versions

Authors:    Adam Williamson <awilliam@redhat.com>

"""

import pytest
from jsonschema.exceptions import ValidationError

import bugzilla2fedmsg.relay


@pytest.fixture(params=[True, False])
def testrelay(request, fakefasjson):
    return bugzilla2fedmsg.relay.MessageRelay(
        {
            "fasjson_url": "https://fasjson.example.com",
            "bugzilla": {"products": ["Fedora", "Fedora EPEL"], "bz4compat": request.param},
        }
    )


def test_bug_create_schema(fakepublish, bug_create_message, testrelay):
    """Check bug.create message schema bits."""
    testrelay.on_stomp_message(bug_create_message["body"], bug_create_message["headers"])
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert message.assigned_to_email == "lvrabec@redhat.com"
    assert message.component_name == "selinux-policy"
    assert message.product_name == "Fedora"
    assert (
        message.summary
        == "dgunchev filed a new bug RHBZ#1701391 'SELinux is preventing touch from 'write'...'"
    )
    assert (
        str(message)
        == "dgunchev filed a new bug RHBZ#1701391 'SELinux is preventing touch from 'write'...'"
    )
    assert message.url == "https://bugzilla.redhat.com/show_bug.cgi?id=1701391"
    assert (
        message.app_icon == "https://bugzilla.redhat.com/extensions/RedHat/web/css/favicon.ico?v=0"
    )
    assert message.agent_name == "dgunchev"
    assert message.app_name == "Bugzilla"
    assert message.usernames == ["dgunchev", "lv"]
    assert message.packages == ["selinux-policy"]
    assert (
        message.agent_avatar
        == "https://seccdn.libravatar.org/avatar/d4bfc5ec5260361c930aad299c8e14fe03af45109ea88e880a191851b8c83e7f?s=64&d=retro"
    )
    assert message._primary_email == "dgunchev@gmail.com"


def test_bug_modify_schema(fakepublish, bug_modify_message, testrelay):
    """Check bug.modify message schema bits."""
    testrelay.on_stomp_message(bug_modify_message["body"], bug_modify_message["headers"])
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "mhroncok@redhat.com updated 'cc' on RHBZ#1699203 'python-pyramid-1.10.4 is available'"
    )
    assert message.usernames == ["adamw", "upstream-release-monitoring"]


def test_bug_modify_four_changes_schema(fakepublish, bug_modify_message_four_changes, testrelay):
    """Check bug.modify message schema bits when the message
    includes four changes (this exercises comma_join).
    """
    testrelay.on_stomp_message(
        bug_modify_message_four_changes["body"],
        bug_modify_message_four_changes["headers"],
    )
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "zebob.m@gmail.com updated 'assigned_to', 'bug_status', 'cc', and 'flag.needinfo' on RHBZ#1702701 'Review Request: perl-Class-AutoClass - D...'"
    )
    assert message.usernames == []


def test_bug_modify_two_changes_schema(fakepublish, bug_modify_message_four_changes, testrelay):
    """Check bug.modify message schema bits when the message
    includes two changes (this exercises a slightly different
    comma_join path).
    """
    # Just dump two changes from the 'four changes' message
    bug_modify_message_four_changes["body"]["event"]["changes"] = bug_modify_message_four_changes[
        "body"
    ]["event"]["changes"][:2]
    testrelay.on_stomp_message(
        bug_modify_message_four_changes["body"],
        bug_modify_message_four_changes["headers"],
    )
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "zebob.m@gmail.com updated 'assigned_to' and 'bug_status' on RHBZ#1702701 'Review Request: perl-Class-AutoClass - D...'"
    )


def test_bug_modify_no_changes_schema(fakepublish, bug_modify_message, testrelay):
    """Check bug.modify message schema bits when event is missing
    'changes' - we often get messages like this, for some reason.
    """
    # wipe the 'changes' dict from the sample message, to simulate
    # one of these broken messages
    del bug_modify_message["body"]["event"]["changes"]
    testrelay.on_stomp_message(bug_modify_message["body"], bug_modify_message["headers"])
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "mhroncok@redhat.com updated something unknown on RHBZ#1699203 'python-pyramid-1.10.4 is available'"
    )
    assert message.usernames == ["upstream-release-monitoring"]


def test_comment_create_schema(fakepublish, comment_create_message, testrelay):
    """Check comment.create message schema bits."""
    testrelay.on_stomp_message(comment_create_message["body"], comment_create_message["headers"])
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "smooge@redhat.com added comment on RHBZ#1691487 'openQA transient test failure as duplica...'"
    )


def test_attachment_create_schema(fakepublish, attachment_create_message, testrelay):
    """Check attachment.create message schema bits."""
    testrelay.on_stomp_message(
        attachment_create_message["body"], attachment_create_message["headers"]
    )
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "peter added attachment on RHBZ#1701353 '[abrt] gnome-software: gtk_widget_unpare...'"
    )


def test_attachment_modify_schema(fakepublish, attachment_modify_message, testrelay):
    """Check attachment.modify message schema bits."""
    testrelay.on_stomp_message(
        attachment_modify_message["body"], attachment_modify_message["headers"]
    )
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "joe updated 'isobsolete' for attachment on RHBZ#1701766 'I2C_HID_QUIRK_NO_IRQ_AFTER_RESET caused ...'"
    )


def test_attachment_modify_no_changes_schema(fakepublish, attachment_modify_message, testrelay):
    """Check attachment.modify message schema bits when event is
    missing 'changes' - unlike the bug.modify case I have not
    actually seen a message like this in the wild, but we do
    handle it just in case.
    """
    # wipe the 'changes' dict from the sample message, to simulate
    # one of these broken messages
    del attachment_modify_message["body"]["event"]["changes"]
    testrelay.on_stomp_message(
        attachment_modify_message["body"], attachment_modify_message["headers"]
    )
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert (
        message.summary
        == "joe updated something unknown for attachment on RHBZ#1701766 'I2C_HID_QUIRK_NO_IRQ_AFTER_RESET caused ...'"
    )


def test_component_not_package_schema(fakepublish, bug_create_message, testrelay):
    """Check we filter out components that aren't packages."""
    # adjust the component in the sample message to one we should
    # filter out
    bug_create_message["body"]["bug"]["component"]["name"] = "distribution"
    testrelay.on_stomp_message(bug_create_message["body"], bug_create_message["headers"])
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    message.validate()
    assert message.packages == []


def test_bug_no_qa_contact(fakepublish, bug_create_message, testrelay):
    """Check bug.create message schema bits when qa_contact is None."""
    bug_create_message["body"]["bug"]["qa_contact"] = None
    testrelay.on_stomp_message(bug_create_message["body"], bug_create_message["headers"])
    assert fakepublish.call_count == 1
    message = fakepublish.call_args[0][0]
    # this should not raise an exception
    try:
        message.validate()
    except ValidationError as e:
        pytest.fail(e)
    assert message.bug["qa_contact"] is None
