# -*- coding: utf-8 -*-
""" Tests for bugzilla2fedmsg.relay.

Authors:    Adam Williamson <awilliam@redhat.com>

"""

import mock
import bugzilla2fedmsg.relay

# sample public bug creation messages
BUGCREATE = {
  "username": None,
  "source_name": "datanommer",
  "certificate": None,
  "i": 0,
  "timestamp": 1555619246.0,
  "msg_id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:8852",
  "crypto": None,
  "topic": "/topic/VirtualTopic.eng.bugzilla.bug.create",
  "headers": {
    "content-length": "1498",
    "expires": "1555705646848",
    "esbMessageType": "bugzillaNotification",
    "timestamp": "1555619246848",
    "original-destination": "/topic/VirtualTopic.eng.bugzilla.bug.create",
    "destination": "/topic/VirtualTopic.eng.bugzilla.bug.create",
    "correlation-id": "06ed3815-4596-49a0-a5a5-1d5b6b7bf01a",
    "priority": "4",
    "subscription": "/queue/Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_destination": "queue://Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_originalDestination": "topic://VirtualTopic.eng.bugzilla.bug.create",
    "message-id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:8852",
    "esbSourceSystem": "bugzilla"
  },
  "signature": None,
  "source_version": "0.9.1",
  "body": {
    "bug": {
      "whiteboard": "abrt_hash:ca3702e55e5d4a4f3057d7a62ad195583a2b9a409990f275a36c87373bd77445;",
      "classification": "Fedora",
      "cf_story_points": "",
      "creation_time": "2019-04-18T20:27:01",
      "target_milestone": None,
      "keywords": [],
      "summary": "SELinux is preventing touch from 'write' accesses on the file /var/log/shorewall-init.log.",
      "cf_ovirt_team": "",
      "cf_release_notes": "",
      "cf_cloudforms_team": "",
      "cf_type": "",
      "cf_fixed_in": "",
      "cf_atomic": "",
      "id": 1701391,
      "priority": "unspecified",
      "platform": "x86_64",
      "version": {
        "id": 5586,
        "name": "29"
      },
      "cf_regression_status": "",
      "cf_environment": "",
      "status": {
        "id": 1,
        "name": "NEW"
      },
      "product": {
        "id": 49,
        "name": "Fedora"
      },
      "qa_contact": {
        "login": "extras-qa@fedoraproject.org",
        "id": 171387,
        "real_name": "Fedora Extras Quality Assurance"
      },
      "reporter": {
        "login": "dgunchev@gmail.com",
        "id": 156190,
        "real_name": "Doncho Gunchev"
      },
      "component": {
        "id": 17100,
        "name": "selinux-policy"
      },
      "cf_category": "",
      "cf_doc_type": "",
      "cf_documentation_action": "",
      "cf_clone_of": "",
      "is_private": False,
      "severity": "unspecified",
      "operating_system": "Unspecified",
      "url": "",
      "last_change_time": "2019-04-18T20:27:01",
      "cf_crm": "",
      "cf_last_closed": None,
      "alias": [],
      "flags": [],
      "assigned_to": {
        "login": "lvrabec@redhat.com",
        "id": 316673,
        "real_name": "Lukas Vrabec"
      },
      "resolution": "",
      "cf_mount_type": ""
    },
    "event": {
      "target": "bug",
      "change_set": "6792.1555619221.41171",
      "routing_key": "bug.create",
      "bug_id": 1701391,
      "user": {
        "login": "dgunchev@gmail.com",
        "id": 156190,
        "real_name": "Doncho Gunchev"
      },
      "time": "2019-04-18T20:27:01",
      "action": "create"
    }
  }
}

# sample public bug modify message
BUGMODIFY = {
  "username": None,
  "source_name": "datanommer",
  "certificate": None,
  "i": 0,
  "timestamp": 1555607535.0,
  "msg_id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:7266",
  "crypto": None,
  "topic": "/topic/VirtualTopic.eng.bugzilla.bug.modify",
  "headers": {
    "content-length": "1556",
    "expires": "1555693935155",
    "esbMessageType": "bugzillaNotification",
    "timestamp": "1555607535155",
    "original-destination": "/topic/VirtualTopic.eng.bugzilla.bug.modify",
    "destination": "/topic/VirtualTopic.eng.bugzilla.bug.modify",
    "correlation-id": "b18f93bb-8a69-4651-8f6b-48a6c323a620",
    "priority": "4",
    "subscription": "/queue/Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_destination": "queue://Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_originalDestination": "topic://VirtualTopic.eng.bugzilla.bug.modify",
    "message-id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:7266",
    "esbSourceSystem": "bugzilla"
  },
  "signature": None,
  "source_version": "0.9.1",
  "body": {
    "bug": {
      "whiteboard": "",
      "classification": "Fedora",
      "cf_story_points": "",
      "creation_time": "2019-04-12T05:49:43",
      "target_milestone": None,
      "keywords": [
        "FutureFeature",
        "Triaged"
      ],
      "summary": "python-pyramid-1.10.4 is available",
      "cf_ovirt_team": "",
      "cf_release_notes": "",
      "cf_cloudforms_team": "",
      "cf_type": "",
      "cf_fixed_in": "",
      "cf_atomic": "",
      "id": 1699203,
      "priority": "unspecified",
      "platform": "Unspecified",
      "version": {
        "id": 495,
        "name": "rawhide"
      },
      "cf_regression_status": "",
      "cf_environment": "",
      "status": {
        "id": 1,
        "name": "NEW"
      },
      "product": {
        "id": 49,
        "name": "Fedora"
      },
      "qa_contact": {
        "login": "extras-qa@fedoraproject.org",
        "id": 171387,
        "real_name": "Fedora Extras Quality Assurance"
      },
      "reporter": {
        "login": "upstream-release-monitoring@fedoraproject.org",
        "id": 282165,
        "real_name": "Upstream Release Monitoring"
      },
      "component": {
        "id": 102174,
        "name": "python-pyramid"
      },
      "cf_category": "",
      "cf_doc_type": "Enhancement",
      "cf_documentation_action": "",
      "cf_clone_of": "",
      "is_private": False,
      "severity": "unspecified",
      "operating_system": "Unspecified",
      "url": "",
      "last_change_time": "2019-04-17T19:11:00",
      "cf_crm": "",
      "cf_last_closed": None,
      "alias": [],
      "flags": [],
      "assigned_to": {
        "login": "infra-sig@lists.fedoraproject.org",
        "id": 370504,
        "real_name": "Fedora Infrastructure SIG"
      },
      "resolution": "",
      "cf_mount_type": ""
    },
    "event": {
      "target": "bug",
      "change_set": "62607.1555607510.78558",
      "routing_key": "bug.modify",
      "bug_id": 1699203,
      "user": {
        "login": "mhroncok@redhat.com",
        "id": 310625,
        "real_name": "Miro Hron\u010dok"
      },
      "time": "2019-04-18T17:11:51",
      "action": "modify",
      "changes": [
        {
          "field": "cc",
          "removed": "",
          "added": "mhroncok@redhat.com"
        }
      ]
    }
  }
}

# sample public comment.create message
COMMENTCREATE = {
  "username": None,
  "source_name": "datanommer",
  "certificate": None,
  "i": 0,
  "timestamp": 1555602948.0,
  "msg_id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:6693",
  "crypto": None,
  "topic": "/topic/VirtualTopic.eng.bugzilla.comment.create",
  "headers": {
    "content-length": "1938",
    "expires": "1555689348470",
    "esbMessageType": "bugzillaNotification",
    "timestamp": "1555602948470",
    "original-destination": "/topic/VirtualTopic.eng.bugzilla.comment.create",
    "destination": "/topic/VirtualTopic.eng.bugzilla.comment.create",
    "correlation-id": "93ab27cf-fada-4e6a-aef5-db7af28b2b71",
    "priority": "4",
    "subscription": "/queue/Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_destination": "queue://Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_originalDestination": "topic://VirtualTopic.eng.bugzilla.comment.create",
    "message-id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:6693",
    "esbSourceSystem": "bugzilla"
  },
  "signature": None,
  "source_version": "0.9.1",
  "body": {
    "comment": {
      "body": "qa09 and qa14 have 8 560 GB SAS drives which are RAID-6 together. \n\nThe systems we get from IBM come through a special contract which in the past required the system to be sent back to add hardware to it. When we added drives it also caused problems because the system didn't match the contract when we returned it. I am checking with IBM on the wearabouts for the systems.",
      "creation_time": "2019-04-18T15:55:38",
      "number": 8,
      "id": 1691487,
      "bug": {
        "whiteboard": "",
        "classification": "Fedora",
        "cf_story_points": "",
        "creation_time": "2019-03-21T17:49:49",
        "target_milestone": None,
        "keywords": [],
        "summary": "openQA transient test failure as duplicated first character just after a snapshot",
        "cf_ovirt_team": "",
        "cf_release_notes": "",
        "cf_cloudforms_team": "",
        "cf_type": "Bug",
        "cf_fixed_in": "",
        "cf_atomic": "",
        "id": 1691487,
        "priority": "unspecified",
        "platform": "ppc64le",
        "version": {
          "id": 5713,
          "name": "30"
        },
        "cf_regression_status": "",
        "cf_environment": "",
        "status": {
          "id": 1,
          "name": "NEW"
        },
        "product": {
          "id": 49,
          "name": "Fedora"
        },
        "qa_contact": {
          "login": "extras-qa@fedoraproject.org",
          "id": 171387,
          "real_name": "Fedora Extras Quality Assurance"
        },
        "reporter": {
          "login": "normand@linux.vnet.ibm.com",
          "id": 364546,
          "real_name": "Michel Normand"
        },
        "component": {
          "id": 145692,
          "name": "openqa"
        },
        "cf_category": "",
        "cf_doc_type": "If docs needed, set a value",
        "cf_documentation_action": "",
        "cf_clone_of": "",
        "is_private": False,
        "severity": "unspecified",
        "operating_system": "Unspecified",
        "url": "",
        "last_change_time": "2019-04-18T15:21:42",
        "cf_crm": "",
        "cf_last_closed": None,
        "alias": [],
        "flags": [],
        "assigned_to": {
          "login": "awilliam@redhat.com",
          "id": 273090,
          "real_name": "Adam Williamson"
        },
        "resolution": "",
        "cf_mount_type": ""
      },
      "is_private": False
    },
    "event": {
      "target": "comment",
      "change_set": "86288.1555602938.43406",
      "routing_key": "comment.create",
      "bug_id": 1691487,
      "user": {
        "login": "smooge@redhat.com",
        "id": 12,
        "real_name": "Stephen John Smoogen"
      },
      "time": "2019-04-18T15:55:38",
      "action": "create"
    }
  }
}

# sample public attachment.create message
ATTACHMENTCREATE = {
  "username": None,
  "source_name": "datanommer",
  "certificate": None,
  "i": 0,
  "timestamp": 1555610522.0,
  "msg_id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:7668",
  "crypto": None,
  "topic": "/topic/VirtualTopic.eng.bugzilla.attachment.create",
  "headers": {
    "content-length": "1883",
    "expires": "1555696922855",
    "esbMessageType": "bugzillaNotification",
    "timestamp": "1555610522855",
    "original-destination": "/topic/VirtualTopic.eng.bugzilla.attachment.create",
    "destination": "/topic/VirtualTopic.eng.bugzilla.attachment.create",
    "correlation-id": "861b24d9-bada-472a-8017-a06bff301595",
    "priority": "4",
    "subscription": "/queue/Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_destination": "queue://Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_originalDestination": "topic://VirtualTopic.eng.bugzilla.attachment.create",
    "message-id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:7668",
    "esbSourceSystem": "bugzilla"
  },
  "signature": None,
  "source_version": "0.9.1",
  "body": {
    "attachment": {
      "description": "File: var_log_messages",
      "file_name": "var_log_messages",
      "is_patch": False,
      "creation_time": "2019-04-18T18:01:51",
      "id": 1556193,
      "flags": [],
      "last_change_time": "2019-04-18T18:01:51",
      "content_type": "text/plain",
      "is_obsolete": False,
      "bug": {
        "whiteboard": "abrt_hash:9045fad863095a5d3f3b387af2b95f43b3482a1d;VARIANT_ID=workstation;",
        "classification": "Fedora",
        "cf_story_points": "",
        "creation_time": "2019-04-18T18:01:33",
        "target_milestone": None,
        "keywords": [],
        "summary": "[abrt] gnome-software: gtk_widget_unparent(): gnome-software killed by SIGSEGV",
        "cf_ovirt_team": "",
        "cf_release_notes": "",
        "cf_cloudforms_team": "",
        "cf_type": "",
        "cf_fixed_in": "",
        "cf_atomic": "",
        "id": 1701353,
        "priority": "unspecified",
        "platform": "x86_64",
        "version": {
          "id": 5713,
          "name": "30"
        },
        "cf_regression_status": "",
        "cf_environment": "",
        "status": {
          "id": 1,
          "name": "NEW"
        },
        "product": {
          "id": 49,
          "name": "Fedora"
        },
        "qa_contact": {
          "login": "extras-qa@fedoraproject.org",
          "id": 171387,
          "real_name": "Fedora Extras Quality Assurance"
        },
        "reporter": {
          "login": "peter@sonniger-tag.eu",
          "id": 361290,
          "real_name": "Peter"
        },
        "component": {
          "id": 126541,
          "name": "gnome-software"
        },
        "cf_category": "",
        "cf_doc_type": "If docs needed, set a value",
        "cf_documentation_action": "",
        "cf_clone_of": "",
        "is_private": False,
        "severity": "unspecified",
        "operating_system": "Unspecified",
        "url": "https://retrace.fedoraproject.org/faf/reports/bthash/f4ca1e58d66fb046d6d1d1b18a84dd779ad34624",
        "last_change_time": "2019-04-18T18:01:50",
        "cf_crm": "",
        "cf_last_closed": None,
        "alias": [],
        "flags": [],
        "assigned_to": {
          "login": "rhughes@redhat.com",
          "id": 213548,
          "real_name": "Richard Hughes"
        },
        "resolution": "",
        "cf_mount_type": ""
      },
      "is_private": False
    },
    "event": {
      "target": "attachment",
      "change_set": "78355.1555610511.09385",
      "routing_key": "attachment.create",
      "bug_id": 1701353,
      "user": {
        "login": "peter@sonniger-tag.eu",
        "id": 361290,
        "real_name": "Peter"
      },
      "time": "2019-04-18T18:01:51",
      "action": "create"
    }
  }
}

# sample private message
PRIVATE = {
  "username": None,
  "source_name": "datanommer",
  "certificate": None,
  "i": 0,
  "timestamp": 1555617948.0,
  "msg_id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:8683",
  "crypto": None,
  "topic": "/topic/VirtualTopic.eng.bugzilla.bug.modify",
  "headers": {
    "content-length": "391",
    "expires": "1555704348944",
    "esbMessageType": "bugzillaNotification",
    "timestamp": "1555617948944",
    "original-destination": "/topic/VirtualTopic.eng.bugzilla.bug.modify",
    "destination": "/topic/VirtualTopic.eng.bugzilla.bug.modify",
    "correlation-id": "1566656e-4163-4d02-856c-9a888ce482d8",
    "priority": "4",
    "subscription": "/queue/Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_destination": "queue://Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_originalDestination": "topic://VirtualTopic.eng.bugzilla.bug.modify",
    "message-id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:8683",
    "esbSourceSystem": "bugzilla"
  },
  "signature": None,
  "source_version": "0.9.1",
  "body": {
    "event": {
      "target": "bug",
      "change_set": "123367.1555617940.83869",
      "routing_key": "bug.modify",
      "bug_id": 1493146,
      "user": {
        "login": "bob@roberts.com",
        "id": 199080,
        "real_name": "Bob Roberts"
      },
      "time": "2019-04-18T20:05:41",
      "action": "modify",
      "changes": [
        {
          "field": "cc",
          "removed": "",
          "added": "bob@roberts.com, rob@boberts.com"
        },
        {
          "field": "flag.needinfo",
          "removed": "",
          "added": "? (rob@boberts.com)"
        }
      ]
    }
  }
}

# sample message for a different product
OTHERPRODUCT = {
  "username": None,
  "source_name": "datanommer",
  "certificate": None,
  "i": 0,
  "timestamp": 1555602888.0,
  "msg_id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:6687",
  "crypto": None,
  "topic": "/topic/VirtualTopic.eng.bugzilla.attachment.create",
  "headers": {
    "content-length": "1744",
    "expires": "1555689288212",
    "esbMessageType": "bugzillaNotification",
    "timestamp": "1555602888212",
    "original-destination": "/topic/VirtualTopic.eng.bugzilla.attachment.create",
    "destination": "/topic/VirtualTopic.eng.bugzilla.attachment.create",
    "correlation-id": "6be413f1-5c44-4598-bca5-c0b07e5a4208",
    "priority": "4",
    "subscription": "/queue/Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_destination": "queue://Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_originalDestination": "topic://VirtualTopic.eng.bugzilla.attachment.create",
    "message-id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-42079-1555559691665-1:361:-1:1:6687",
    "esbSourceSystem": "bugzilla"
  },
  "signature": None,
  "source_version": "0.9.1",
  "body": {
    "attachment": {
      "description": "journalctl/systemctl output",
      "file_name": "kubelet.tgz",
      "is_patch": False,
      "creation_time": "2019-04-18T15:54:39",
      "id": 1556163,
      "flags": [],
      "last_change_time": "2019-04-18T15:54:39",
      "content_type": "application/gzip",
      "is_obsolete": False,
      "bug": {
        "whiteboard": "",
        "classification": "Red Hat",
        "cf_story_points": "",
        "creation_time": "2019-04-18T15:46:21",
        "target_milestone": None,
        "keywords": [],
        "summary": "One master shows not ready out of 3 after several hours post deployment.",
        "cf_ovirt_team": "",
        "cf_release_notes": "",
        "cf_cloudforms_team": "",
        "cf_type": "Bug",
        "cf_fixed_in": "",
        "cf_atomic": "",
        "id": 1701324,
        "priority": "unspecified",
        "platform": "Unspecified",
        "version": {
          "id": 5777,
          "name": "unspecified"
        },
        "cf_regression_status": "",
        "cf_environment": "",
        "status": {
          "id": 1,
          "name": "NEW"
        },
        "product": {
          "id": 561,
          "name": "Kubernetes-native Infrastructure"
        },
        "qa_contact": {
          "login": "achernet@redhat.com",
          "id": 391433,
          "real_name": "Arik Chernetsky"
        },
        "reporter": {
          "login": "sasha@redhat.com",
          "id": 309636,
          "real_name": "Alexander Chuzhoy"
        },
        "component": {
          "id": 180277,
          "name": "Deployment"
        },
        "cf_category": "",
        "cf_doc_type": "If docs needed, set a value",
        "cf_documentation_action": "",
        "cf_clone_of": "",
        "is_private": False,
        "severity": "unspecified",
        "operating_system": "Unspecified",
        "url": "",
        "last_change_time": "2019-04-18T15:46:40",
        "cf_crm": "",
        "cf_last_closed": None,
        "alias": [],
        "flags": [],
        "assigned_to": {
          "login": "athomas@redhat.com",
          "id": 56702,
          "real_name": "Angus Thomas"
        },
        "resolution": "",
        "cf_mount_type": ""
      },
      "is_private": False
    },
    "event": {
      "target": "attachment",
      "change_set": "33145.1555602879.56178",
      "routing_key": "attachment.create",
      "bug_id": 1701324,
      "user": {
        "login": "sasha@redhat.com",
        "id": 309636,
        "real_name": "Alexander Chuzhoy"
      },
      "time": "2019-04-18T15:54:39",
      "action": "create"
    }
  }
}


class TestRelay(object):
    relay = bugzilla2fedmsg.relay.MessageRelay({'bugzilla': {'products': ["Fedora", "Fedora EPEL"]}})

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_bug_create(self, fakepublish):
        """Check correct result for bug.create message."""
        self.relay.on_stomp_message(BUGCREATE['body'], BUGCREATE['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.topic == 'bugzilla.bug.new'
        assert 'product' in message.body['bug']
        assert message.body['event']['routing_key'] == "bug.create"
        # check 'creator' backwards compat
        assert message.body['bug']['creator'] == "dgunchev@gmail.com"
        # check 'op_sys' backwards compat
        assert message.body['bug']['op_sys'] == "Unspecified"
        # this tests convert_datetimes
        createtime = message.body['bug']['creation_time']
        assert createtime == 1555619221.0

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_bug_modify(self, fakepublish):
        """Check correct result for bug.modify message."""
        self.relay.on_stomp_message(BUGMODIFY['body'], BUGMODIFY['headers'])
        assert fakepublish.call_count == 1
        message = fakepublish.call_args[0][0]
        assert message.topic == 'bugzilla.bug.update'
        assert 'product' in message.body['bug']
        assert message.body['event']['routing_key'] == "bug.modify"

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_comment_create(self, fakepublish):
        """Check correct result for comment.create message."""
        self.relay.on_stomp_message(COMMENTCREATE['body'], COMMENTCREATE['headers'])
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
    def test_attachment_create(self, fakepublish):
        """Check correct result for attachment.create message."""
        self.relay.on_stomp_message(ATTACHMENTCREATE['body'], ATTACHMENTCREATE['headers'])
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
    def test_private_drop(self, fakepublish):
        """Check that we drop (don't publish) a private message."""
        self.relay.on_stomp_message(PRIVATE['body'], PRIVATE['headers'])
        assert fakepublish.call_count == 0

    @mock.patch('bugzilla2fedmsg.relay.publish', autospec=True)
    def test_other_product_drop(self, fakepublish):
        """Check that we drop (don't publish) a message for a product
        we don't want to cover. As our fake hub doesn't really have a
        config, the products we care about are the defaults: 'Fedora'
        and 'Fedora EPEL'.
        """
        self.relay.on_stomp_message(OTHERPRODUCT['body'], OTHERPRODUCT['headers'])
        assert fakepublish.call_count == 0
