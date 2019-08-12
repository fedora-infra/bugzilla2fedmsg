Changelog
=========

.. Generate with git log --no-merges --pretty='format:- %s `%h <https://github.com/fedora-infra/bugzilla2fedmsg/commit/%H>`_' last-tag..

1.0.0
-----

- Add missing dependency `8bf12ee <https://github.com/fedora-infra/bugzilla2fedmsg/commit/8bf12eec6c311588241f1599124bc783f2556a93>`_
- Drop support for Python 3.4 `b5b9c0b <https://github.com/fedora-infra/bugzilla2fedmsg/commit/b5b9c0b93bc0f3d3771889b9e87243a6e2a7c8c1>`_
- Implement message schemas `d0b799a <https://github.com/fedora-infra/bugzilla2fedmsg/commit/d0b799a0be6b8249fb2ce7b89d0f2a03b8547073>`_
- Make Bugzilla 4 backwards compatibility transformation optional `424afa5 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/424afa56565e025799e091520d333ec14779a660>`_
- Extend backwards compatibility a bit `319e06a <https://github.com/fedora-infra/bugzilla2fedmsg/commit/319e06ac2627d75c30d1796492b8c050eb7bffef>`_
- Make test messages into pytest fixtures `30d6950 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/30d695016874695ad3de1687630718c10fffe5e0>`_
- Don't 'organize' the message as it comes off the BZ wire `4f43653 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/4f436530393502765ab16c5b640ada12a3ecbbf1>`_
- Add tests for handling of exceptions from publish() `ee0c4c8 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/ee0c4c83558216ae09490ad0f75a4fad08f90557>`_
- Don't try and publish datetimes `73c9176 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/73c9176ad59008181468d412fe11119e317dab64>`_
- Add test for attachment.create message `3af89d2 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/3af89d2d4aec14a1b459312b6a987a7eb1dc5588>`_
- Also handle backwards compatibility for operating system `9deb916 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/9deb916383707044a0839ccaf845cba897ab9896>`_
- Handle 'reporter' vs. 'creator' with backwards compat `19fd1b4 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/19fd1b4ff961b3f567527ec39768f425e42484a2>`_
- Fix convert_datetimes for Bugzilla 5.0 messages `f386c7e <https://github.com/fedora-infra/bugzilla2fedmsg/commit/f386c7ea51173e0945aa3d6c5067145df0ae71f6>`_
- Fix decision as to whether this is a 'new bug' event `7fd1fc5 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/7fd1fc52f567aa2ae090425580503fd5de4faf8a>`_
- Add a test suite `7d4352e <https://github.com/fedora-infra/bugzilla2fedmsg/commit/7d4352e0dbf0a694a2c0b9518d898d3446fae027>`_
- Handle comments and other 'objects' for Bugzilla 5+ messages `aa98152 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/aa981520c24f1183ec52f1af513ed8f4254a19b7>`_
- Bump version `122ce19 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/122ce19570618ddcef3f7b3e6045020f41f16fb6>`_
- Improve the setup.py `5bb8cb5 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/5bb8cb551dd88a70aaa2d3c4daa1d670039f7013>`_
- Adapt to STOMP protocol 1.2 `25e2d20 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/25e2d2040eb3492ac1038c29d309851570d8cfba>`_
- Send and receive STOMP heartbeats `c67c49c <https://github.com/fedora-infra/bugzilla2fedmsg/commit/c67c49cc349629c7338a3e795c1fdcdc7b873aa9>`_
- Handle duplicate subscriptions on reconnection `d04e8ce <https://github.com/fedora-infra/bugzilla2fedmsg/commit/d04e8ce6f71a16cdef2436e921957109b30627d7>`_
- Migrate to Fedora Messaging `f2596f2 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/f2596f2cba5885d5c6cf60c3a6dbe99b281eb54e>`_
- Fix CI `9646437 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/9646437cea7c3569614dbeb0d5b47208404b59be>`_

0.3.1
-----

- Use Tox and Jenkins `d26645e <https://github.com/fedora-infra/bugzilla2fedmsg/commit/d26645e78f36bd3288300f5373dd4f80d4fff767>`_
- Update for bz5. `ee54877 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/ee548775f099dbf5ee0fdf33643dcaa2ae745665>`_
- Pass along STOMP headers, if we have them. `018492a <https://github.com/fedora-infra/bugzilla2fedmsg/commit/018492a27b1b5afa669f77e59c5da45adb738cb9>`_
- No more attachments. `84cd372 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/84cd37207be77228192efa2c3fdb54eb190e1b6a>`_
- Make all timestamps comparable. `35b5900 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/35b5900c156b4c6fca401ab2097879d98761befe>`_
- use the full name here. `b6cccd1 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/b6cccd16bef2dcfa6ea7239b6b2099ae99ba92dc>`_
- Fix broken import. `ce290be <https://github.com/fedora-infra/bugzilla2fedmsg/commit/ce290beedbae80e146f06752a4683413ad3007e9>`_

0.3.0
-----

Pull Requests

- (@ralphbean)      #5, Look before you leap.
  https://github.com/fedora-infra/bugzilla2fedmsg/pull/5
- (@ralphbean)      #6, Got moved again.
  https://github.com/fedora-infra/bugzilla2fedmsg/pull/6

Commits

- 8c0080ec9 Remove unused import.
  https://github.com/fedora-infra/bugzilla2fedmsg/commit/8c0080ec9
- 9ede5ffab Look before you leap.
  https://github.com/fedora-infra/bugzilla2fedmsg/commit/9ede5ffab
- 1863f1959 Got moved again.
  https://github.com/fedora-infra/bugzilla2fedmsg/commit/1863f1959

0.2.1
-----

- Handle timezones. `ff44f64b5 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/ff44f64b5152f56277a4e498dbf6426aa16b51e6>`_
- Merge pull request #4 from fedora-infra/feature/timezones `88581d44a <https://github.com/fedora-infra/bugzilla2fedmsg/commit/88581d44a662c1532d47f0cf87299afbb1ceef47>`_

0.2.0
-----

- Ignore certs and stuff. `6c92062bd <https://github.com/fedora-infra/bugzilla2fedmsg/commit/6c92062bd7f1b119f6d8f47e9e09cd15467bb625>`_
- Document stomp ssl options. `15f1e150b <https://github.com/fedora-infra/bugzilla2fedmsg/commit/15f1e150b7668d03f7544856adf5b5b6816cfc52>`_
- Now with failover().. `244f4c7d8 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/244f4c7d82a890545165e7347b80bc82d7db44cd>`_
- This got changed on us. `40f025956 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/40f0259566e57c6954d35e14b160e906e2304a21>`_
- Enhance bugzilla messages. `96d981275 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/96d9812755e3fa9ffb0758b49195040da627a372>`_
- Remove our own threading stuff. `31b243172 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/31b243172e37ff194082eaa8bee5b565ff843912>`_
- Also, give the consumer a couple extra endpoints for development. `be6f076d8 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/be6f076d871e4d5187c35e3985edafb0f1bc9c08>`_
- Merge pull request #1 from fedora-infra/feature/enhanced-bugzilla `94d9d4bad <https://github.com/fedora-infra/bugzilla2fedmsg/commit/94d9d4bad827708fbb0dca7937a19e9e0fd321c4>`_
- Merge pull request #2 from fedora-infra/feature/de-threaded `90727a2c7 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/90727a2c77863f396b43147756e757fba00f9dbc>`_

0.1.3
-----

- License LGPLv2+. `31a552b35 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/31a552b35b873243cf9b013bdf2e6f9ab3bc6bea>`_

0.1.2
-----

- Include .rst files. `709584ff2 <https://github.com/fedora-infra/bugzilla2fedmsg/commit/709584ff27146a4bffa445efa3a50506e8b4093c>`_
