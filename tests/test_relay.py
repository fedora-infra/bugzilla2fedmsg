# -*- coding: utf-8 -*-
""" Tests for bugzilla2fedmsg.relay.

Authors:    Adam Williamson <awilliam@redhat.com>

"""

import mock
import bugzilla2fedmsg.relay
import fedora_messaging.exceptions


class TestRelay(object):
    relay = bugzilla2fedmsg.relay.MessageRelay({'bugzilla': {'products': ["Fedora", "Fedora EPEL"]}})

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_bug_create(self, fakepublish, bug_create_message):
        """Check correct result for bug.create message."""
        self.relay.on_stomp_message(bug_create_message['body'], bug_create_message['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.topic == 'bugzilla.bug.new'
        assert 'product' in message.body['bug']
        assert message.body['event']['routing_key'] == "bug.create"
        # this tests convert_datetimes
        createtime = message.body['bug']['creation_time']
        assert createtime == 1555619221.0

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_bug_modify(self, fakepublish, bug_modify_message):
        """Check correct result for bug.modify message."""
        self.relay.on_stomp_message(bug_modify_message['body'], bug_modify_message['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.topic == 'bugzilla.bug.update'
        assert 'product' in message.body['bug']
        assert message.body['event']['routing_key'] == "bug.modify"

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_comment_create(self, fakepublish, comment_create_message):
        """Check correct result for comment.create message."""
        self.relay.on_stomp_message(comment_create_message['body'], comment_create_message['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.topic == 'bugzilla.bug.update'
        assert message.body['comment'] == {
            "author": "smooge@redhat.com",
            "body": "qa09 and qa14 have 8 560 GB SAS drives which are RAID-6 together. \n\nThe systems we get from IBM come through a special contract which in the past required the system to be sent back to add hardware to it. When we added drives it also caused problems because the system didn't match the contract when we returned it. I am checking with IBM on the wearabouts for the systems.",
            "creation_time": 1555602938.0,
            "number": 8,
            "id": 1691487,
            "is_private": False,
        }
        # we probably don't need to check these whole things...
        assert 'product' in message.body['bug']
        assert message.body['event']['routing_key'] == "comment.create"

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_attachment_create(self, fakepublish, attachment_create_message):
        """Check correct result for attachment.create message."""
        self.relay.on_stomp_message(attachment_create_message['body'], attachment_create_message['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.topic == 'bugzilla.bug.update'
        assert message.body['attachment'] == {
            "description": "File: var_log_messages",
            "file_name": "var_log_messages",
            "is_patch": False,
            "creation_time": 1555610511.0,
            "id": 1556193,
            "flags": [],
            "last_change_time": 1555610511.0,
            "content_type": "text/plain",
            "is_obsolete": False,
            "is_private": False,
        }
        # we probably don't need to check these whole things...
        assert 'product' in message.body['bug']
        assert message.body['event']['routing_key'] == "attachment.create"

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_private_drop(self, fakepublish, private_message):
        """Check that we drop (don't publish) a private message."""
        self.relay.on_stomp_message(private_message['body'], private_message['headers'])
        assert fakepublish.call_count == 0

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_other_product_drop(self, fakepublish, other_product_message):
        """Check that we drop (don't publish) a message for a product
        we don't want to cover. As our fake hub doesn't really have a
        config, the products we care about are the defaults: 'Fedora'
        and 'Fedora EPEL'.
        """
        self.relay.on_stomp_message(other_product_message['body'], other_product_message['headers'])
        assert fakepublish.call_count == 0

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_bz4_compat(self, fakepublish, bug_create_message, comment_create_message):
        """This tests various modifications we make to the bug dict in
        the name of 'backwards compatibility', i.e. making messages
        look more like they did before Bugzilla 5.
        """
        bz4relay = bugzilla2fedmsg.relay.MessageRelay(
            {'bugzilla': {'products': ["Fedora", "Fedora EPEL"], 'bz4compat': True}})
        bz4relay.on_stomp_message(bug_create_message['body'], bug_create_message['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.body['bug']['assigned_to'] == "lvrabec@redhat.com"
        assert message.body['bug']['component'] == "selinux-policy"
        assert message.body['bug']['product'] == "Fedora"
        assert message.body['bug']['cc'] == []
        assert message.body['bug']['creator'] == "dgunchev@gmail.com"
        assert message.body['bug']['op_sys'] == "Unspecified"
        assert message.body['event']['who'] == "dgunchev@gmail.com"
        assert message.body['bug']['weburl'] == "https://bugzilla.redhat.com/show_bug.cgi?id=1701391"
        # we need a comment message to test this
        fakepublish.reset_mock()
        self.relay.on_stomp_message(comment_create_message['body'], comment_create_message['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.body['comment']['author'] == "smooge@redhat.com"

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_bz4_compat_disabled(self, fakepublish, bug_create_message, comment_create_message):
        """Test that we *don't* make Bugzilla 4 compat modifications
        if the option is switched off. Tests only the destructive ones
        as they're the ones we really want to avoid, and if these
        aren't happening it's pretty certain the others aren't either.
        """
        nobz4relay = bugzilla2fedmsg.relay.MessageRelay(
            {'bugzilla': {'products': ["Fedora", "Fedora EPEL"], 'bz4compat': False}})
        nobz4relay.on_stomp_message(bug_create_message['body'], bug_create_message['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert all(item in message.body['bug']['assigned_to'] for item in ('login', 'id', 'real_name'))
        assert all(item in message.body['bug']['component'] for item in ('id', 'name'))
        assert all(item in message.body['bug']['product'] for item in ('id', 'name'))

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_publish_exception_publishreturned(self, fakepublish, bug_create_message, caplog):
        """Check that we handle PublishReturned exception from publish
        correctly.
        """
        fakepublish.side_effect = fedora_messaging.exceptions.PublishReturned("oops!")
        # this should not raise any exception
        self.relay.on_stomp_message(bug_create_message['body'], bug_create_message['headers'])
        assert fakepublish.call_count == 1
        # check the logging worked
        assert "Fedora Messaging broker rejected message" in caplog.text

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_publish_exception_connectionexception(self, fakepublish, bug_create_message, caplog):
        """Check that we handle ConnectionException from publish
        correctly.
        """
        # First test PublishReturned
        fakepublish.side_effect = fedora_messaging.exceptions.ConnectionException("oops!")
        # this should not raise any exception
        self.relay.on_stomp_message(bug_create_message['body'], bug_create_message['headers'])
        assert fakepublish.call_count == 1
        # check the logging worked
        assert "Error sending message" in caplog.text
