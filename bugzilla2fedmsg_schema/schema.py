"""fedora-messaging schema for bugzilla2fedmsg."""

import copy

from fedora_messaging import message
from fedora_messaging.schema_utils import libravatar_url
from .utils import comma_join, email_to_fas


class BaseMessage(message.Message):
    """
    Base message class for all message versions and variants.
    """

    def __str__(self):
        """We just use the summary for now."""
        return self.summary

    @property
    def summary(self):
        """A summary of the message."""
        (user, _) = email_to_fas(self._primary_email)
        idx = self.bug['id']
        title = self.bug['summary']
        action = self.body['event']['action']
        target = self.body['event']['target']

        if len(title) > 40:
            title = title[:40] + "..."

        if target == "bug" and action == "create":
            tmpl = "{user} filed a new bug RHBZ#{idx} '{title}'"
            return tmpl.format(user=user, idx=idx, title=title)

        elif self.body['event']['action'] == "create":
            tmpl = "{user} added {target} on RHBZ#{idx} '{title}'"
            return tmpl.format(user=user, target=target, idx=idx, title=title)

        # at this point 'action' must be "modify": we're modifying the
        # target
        fields = [d['field'] for d in self.body['event'].get('changes', [])]
        fields = comma_join(fields)
        if target == "bug":
            tmpl = "{user} updated {fields} on RHBZ#{idx} '{title}'"
            return tmpl.format(user=user, fields=fields, idx=idx, title=title)
        tmpl = "{user} updated {fields} for {target} on RHBZ#{idx} '{title}'"
        return tmpl.format(user=user, fields=fields, target=target, idx=idx, title=title)

    @property
    def url(self):
        """The URL for the bug.

        Returns:
            str: A relevant URL.
        """
        return "https://bugzilla.redhat.com/show_bug.cgi?id={}".format(self.bug['id'])

    @property
    def app_icon(self):
        """An URL to the icon of the application that generated the message."""
        return "https://bugzilla.redhat.com/extensions/RedHat/web/css/favicon.ico?v=0"

    @property
    def usernames(self):
        """List of users affected by the action that generated this message."""
        users = set()
        emails = self._all_emails
        for email in emails:
            (user, is_fas) = email_to_fas(email)
            if is_fas:
                users.add(user)
        return list(users)

    @property
    def packages(self):
        """List of packages affected by the action that generated this message."""
        compname = self.component_name
        # these are Bugzilla components that are not Fedora packages
        # add any more you can think of
        notpackages = [
            'distribution',
            'LiveCD',
            'LiveCD - FEL',
            'LiveCD - Games',
            'LiveCD - KDE',
            'LiveCD - LXDE',
            'LiveCD - Xfce',
            'Package Review',
        ]
        if compname in notpackages:
            return []
        return [compname]

    @property
    def agent_avatar(self):
        """URL to the avatar of the user who caused the action."""
        return libravatar_url(self._primary_email)

    @property
    def _primary_email(self):
        """The email for the primary user associated with the action
        that generated this message.
        """
        return self.body['event']['user']['login']

    @property
    def _all_emails(self):
        """List of email addresses of all users relevant to the action
        that generated this message.
        """
        users = set()

        # user from the event dict: person who triggered the event
        users.add(self._primary_email)

        # bug reporter and assignee
        users.add(self.bug['reporter']['login'])
        users.add(self.assigned_to_email)

        for change in self.body['event'].get('changes', []):
            if change['field'] == "cc":
                # anyone added to CC list
                for user in change['added'].split(','):
                    user.strip()
                    if user:
                        users.add(user)
            elif change['field'] == "flag.needinfo":
                # anyone for whom a 'needinfo' flag is set
                # this is extracting the email from a value like:
                # "? (senrique@redhat.com)"
                user = change['added'].split('(', 1)[1].rsplit(')', 1)[0]
                if user:
                    users.add(user)

        # Strip anything that made it in erroneously
        for user in list(users):
            if user.endswith('lists.fedoraproject.org'):
                users.remove(user)

        users = list(users)
        users.sort()
        return users


class MessageV1(BaseMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by Bugzilla. This schema is accurate for messages emitted since
    bugzilla2fedmsg commit 08b3e0c5 with Bugzilla 4 compatibility DISABLED.
    """

    body_schema = {
        "id": "http://fedoraproject.org/message-schema/bugzilla2fedmsg#",
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for message sent by Bugzilla (v1, BZ4 compat disabled)",
        "type": "object",
        "properties": {
            "bug": {
                "description": "An object representing the relevant bug itself",
                "type": "object",
                "properties": {
                    "alias": {"type": "array"},
                    "assigned_to": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "login": {"type": "string"},
                            "real_name": {"type": "string"},
                        },
                    },
                    "classification": {"type": "string"},
                    "component": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "name": {"type": "string"},
                        },
                    },
                    "creation_time": {"type": "number"},
                    "flags": {"type": "array"},
                    "id": {"type": "number"},
                    "is_private": {"type": "boolean"},
                    "keywords": {"type": "array"},
                    "last_change_time": {"type": "number"},
                    "operating_system": {"type": "string"},
                    "platform": {"type": "string"},
                    "priority": {"type": "string"},
                    "product": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "name": {"type": "string"},
                        },
                    },
                    "qa_contact": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "login": {"type": "string"},
                            "real_name": {"type": "string"},
                        },
                    },
                    "reporter": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "login": {"type": "string"},
                            "real_name": {"type": "string"},
                        },
                    },
                    "resolution": {"type": "string"},
                    "severity": {"type": "string"},
                    "status": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "name": {"type": "string"},
                        },
                    },
                    "summary": {"type": "string"},
                    "url": {"type": "string"},
                    "version": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "name": {"type": "string"},
                        },
                    },
                    "whiteboard": {"type": "string"},
                },
                "required": ["alias", "assigned_to", "classification", "component",
                             "creation_time", "flags", "id", "is_private", "keywords",
                             "last_change_time", "operating_system", "platform", "priority",
                             "product", "qa_contact", "reporter", "resolution", "severity",
                             "status", "summary", "url", "version", "whiteboard"],
            },
            "event": {
                "description": "An object representing the event the message relates to",
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "bug_id": {"type": "number"},
                    "changes": {"type": "array"},
                    "change_set": {"type": "string"},
                    "routing_key": {"type": "string"},
                    "rule_id": {"type": "number"},
                    "target": {"type": "string"},
                    "time": {"type": "number"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "login": {"type": "string"},
                            "real_name": {"type": "string"},
                        },
                    },
                },
                "required": ["action", "bug_id", "change_set", "routing_key", "target",
                             "time", "user"],
            },
            "comment": {
                "description": "An object representing a comment affected by the event",
                "type": "object",
                "properties": {
                    "body": {"type": "string"},
                    "creation_time": {"type": "number"},
                    "id": {"type": "number"},
                    "is_private": {"type": "boolean"},
                    "number": {"type": "number"},
                },
                "required": ["body", "creation_time", "id", "is_private", "number"],
            },
            "attachment": {
                "description": "An object representing an attachment affected by the event",
                "properties": {
                    "content_type": {"type": "string"},
                    "creation_time": {"type": "number"},
                    "description": {"type": "string"},
                    "file_name": {"type": "string"},
                    "flags": {"type": "array"},
                    "id": {"type": "number"},
                    "is_obsolete": {"type": "boolean"},
                    "is_patch": {"type": "boolean"},
                    "is_private": {"type": "boolean"},
                    "last_change_time": {"type": "number"},
                },
                "required": ["content_type", "creation_time", "description", "file_name",
                             "flags", "id", "is_obsolete", "is_patch", "is_private",
                             "last_change_time"],
            },
        },
        "required": ["bug", "event"],
    }

    @property
    def bug(self):
        """The bug dictionary from the message."""
        return self.body['bug']

    @property
    def assigned_to_email(self):
        """The email address of the user to which the bug is assigned."""
        return self.bug['assigned_to']['login']

    @property
    def component_name(self):
        """The name of the component against which the bug is filed."""
        return self.bug['component']['name']

    @property
    def product_name(self):
        """The name of the product against which the bug is filed."""
        return self.bug['product']['name']


class MessageV1BZ4(MessageV1):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by Bugzilla. This schema is accurate for messages emitted since
    bugzilla2fedmsg commit 08b3e0c5 with Bugzilla 4 compatibility ENABLED.
    """

    body_schema = copy.deepcopy(MessageV1.body_schema)
    bug = body_schema["properties"]["bug"]
    event = body_schema["properties"]["event"]
    comment = body_schema["properties"]["comment"]
    bug["properties"]["assigned_to"] = {"type": "string"}
    bug["properties"]["component"] = {"type": "string"}
    bug["properties"]["product"] = {"type": "string"}
    bug["properties"]["cc"] = {"type": "array"}
    bug["properties"]["creator"] = {"type": "string"}
    bug["properties"]["op_sys"] = {"type": "string"}
    bug["properties"]["weburl"] = {"type": "string"}
    bug["required"].extend(["cc", "weburl"])
    event["properties"]["who"] = {"type": "string"}
    event["required"].append("who")
    comment["properties"]["author"] = {"type": "string"}
    comment["required"].append("author")

    @property
    def bug(self):
        """The bug dictionary from the message."""
        return self.body['bug']

    @property
    def assigned_to_email(self):
        """The email address of the user to which the bug is assigned."""
        return self.bug['assigned_to']

    @property
    def component_name(self):
        """The name of the component against which the bug is filed."""
        return self.bug['component']

    @property
    def product_name(self):
        """The name of the product against which the bug is filed."""
        return self.bug['product']
