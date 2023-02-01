# -*- coding: utf-8 -*-
""" Tests for bugzilla2fedmsg_schemas.

Authors:    Adam Williamson <awilliam@redhat.com>

"""

from unittest import mock

import pytest
from jsonschema.exceptions import ValidationError

import bugzilla2fedmsg.relay


class TestSchemas(object):
    # We are basically going to use the relays to construct messages
    # just as we do in test_relay, then check the messages validate
    # and test the various schema methods. We parametrize the tests
    # to test all the schema versions
    bz4relay = bugzilla2fedmsg.relay.MessageRelay(
        {"bugzilla": {"products": ["Fedora", "Fedora EPEL"], "bz4compat": True}}
    )
    nobz4relay = bugzilla2fedmsg.relay.MessageRelay(
        {"bugzilla": {"products": ["Fedora", "Fedora EPEL"], "bz4compat": False}}
    )

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_bug_create_schema(self, fakepublish, bug_create_message, relay):
        """Check bug.create message schema bits."""
        relay.on_stomp_message(
            bug_create_message["body"], bug_create_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert message.assigned_to_email == "lvrabec@redhat.com"
        assert message.component_name == "selinux-policy"
        assert message.product_name == "Fedora"
        assert (
            message.summary
            == "dgunchev@gmail.com filed a new bug RHBZ#1701391 'SELinux is preventing touch from 'write'...'"
        )
        assert (
            str(message)
            == "dgunchev@gmail.com filed a new bug RHBZ#1701391 'SELinux is preventing touch from 'write'...'"
        )
        assert message.url == "https://bugzilla.redhat.com/show_bug.cgi?id=1701391"
        assert (
            message.app_icon
            == "https://bugzilla.redhat.com/extensions/RedHat/web/css/favicon.ico?v=0"
        )
        assert message.agent_name == "Doncho Gunchev"
        assert message.app_name == "bugzilla2fedmsg"
        # broken till we can do email2fas
        assert message.usernames == []
        assert message.packages == ["selinux-policy"]
        assert (
            message.agent_avatar
            == "https://seccdn.libravatar.org/avatar/d4bfc5ec5260361c930aad299c8e14fe03af45109ea88e880a191851b8c83e7f?s=64&d=retro"
        )
        assert message._primary_email == "dgunchev@gmail.com"
        assert message._all_emails == ["dgunchev@gmail.com", "lvrabec@redhat.com"]

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_bug_modify_schema(self, fakepublish, bug_modify_message, relay):
        """Check bug.modify message schema bits."""
        relay.on_stomp_message(
            bug_modify_message["body"], bug_modify_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert (
            message.summary
            == "mhroncok@redhat.com updated 'cc' on RHBZ#1699203 'python-pyramid-1.10.4 is available'"
        )
        # here we test both picking up an address from a 'cc' change
        # event, and filtering out lists.fedoraproject.org addresses
        assert message._all_emails == [
            "awilliam@redhat.com",
            "mhroncok@redhat.com",
            "upstream-release-monitoring@fedoraproject.org",
        ]
        # here we test that we can at least derive usernames from
        # fedoraproject.org email addresses
        assert message.usernames == ["upstream-release-monitoring"]

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_bug_modify_four_changes_schema(
        self, fakepublish, bug_modify_message_four_changes, relay
    ):
        """Check bug.modify message schema bits when the message
        includes four changes (this exercises comma_join).
        """
        relay.on_stomp_message(
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
        # this tests gathering an address from a 'needinfo' change
        assert message._all_emails == [
            "ppisar@redhat.com",
            "rob@boberts.com",
            "zebob.m@gmail.com",
        ]

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_bug_modify_two_changes_schema(
        self, fakepublish, bug_modify_message_four_changes, relay
    ):
        """Check bug.modify message schema bits when the message
        includes two changes (this exercises a slightly different
        comma_join path).
        """
        # Just dump two changes from the 'four changes' message
        bug_modify_message_four_changes["body"]["event"][
            "changes"
        ] = bug_modify_message_four_changes["body"]["event"]["changes"][:2]
        relay.on_stomp_message(
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

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_bug_modify_no_changes_schema(self, fakepublish, bug_modify_message, relay):
        """Check bug.modify message schema bits when event is missing
        'changes' - we often get messages like this, for some reason.
        """
        # wipe the 'changes' dict from the sample message, to simulate
        # one of these broken messages
        del bug_modify_message["body"]["event"]["changes"]
        relay.on_stomp_message(
            bug_modify_message["body"], bug_modify_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert (
            message.summary
            == "mhroncok@redhat.com updated something unknown on RHBZ#1699203 'python-pyramid-1.10.4 is available'"
        )
        assert message._all_emails == [
            "mhroncok@redhat.com",
            "upstream-release-monitoring@fedoraproject.org",
        ]

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_comment_create_schema(self, fakepublish, comment_create_message, relay):
        """Check comment.create message schema bits."""
        relay.on_stomp_message(
            comment_create_message["body"], comment_create_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert (
            message.summary
            == "smooge@redhat.com added comment on RHBZ#1691487 'openQA transient test failure as duplica...'"
        )

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_attachment_create_schema(
        self, fakepublish, attachment_create_message, relay
    ):
        """Check attachment.create message schema bits."""
        relay.on_stomp_message(
            attachment_create_message["body"], attachment_create_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert (
            message.summary
            == "peter@sonniger-tag.eu added attachment on RHBZ#1701353 '[abrt] gnome-software: gtk_widget_unpare...'"
        )

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_attachment_modify_schema(
        self, fakepublish, attachment_modify_message, relay
    ):
        """Check attachment.modify message schema bits."""
        relay.on_stomp_message(
            attachment_modify_message["body"], attachment_modify_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert (
            message.summary
            == "joequant@gmail.com updated 'isobsolete' for attachment on RHBZ#1701766 'I2C_HID_QUIRK_NO_IRQ_AFTER_RESET caused ...'"
        )

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_attachment_modify_no_changes_schema(
        self, fakepublish, attachment_modify_message, relay
    ):
        """Check attachment.modify message schema bits when event is
        missing 'changes' - unlike the bug.modify case I have not
        actually seen a message like this in the wild, but we do
        handle it just in case.
        """
        # wipe the 'changes' dict from the sample message, to simulate
        # one of these broken messages
        del attachment_modify_message["body"]["event"]["changes"]
        relay.on_stomp_message(
            attachment_modify_message["body"], attachment_modify_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert (
            message.summary
            == "joequant@gmail.com updated something unknown for attachment on RHBZ#1701766 'I2C_HID_QUIRK_NO_IRQ_AFTER_RESET caused ...'"
        )

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_component_not_package_schema(self, fakepublish, bug_create_message, relay):
        """Check we filter out components that aren't packages."""
        # adjust the component in the sample message to one we should
        # filter out
        bug_create_message["body"]["bug"]["component"]["name"] = "distribution"
        relay.on_stomp_message(
            bug_create_message["body"], bug_create_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        message.validate()
        assert message.packages == []

    @pytest.mark.parametrize("relay", (bz4relay, nobz4relay))
    @mock.patch("bugzilla2fedmsg.relay.publish", autospec=True)
    def test_bug_no_qa_contact(self, fakepublish, bug_create_message, relay):
        """Check bug.create message schema bits when qa_contact is None."""
        bug_create_message["body"]["bug"]["qa_contact"] = None
        relay.on_stomp_message(
            bug_create_message["body"], bug_create_message["headers"]
        )
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        # this should not raise an exception
        try:
            message.validate()
        except ValidationError as e:
            assert False, e
        assert message.bug["qa_contact"] is None
