#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='bugzilla2fedmsg',
    version='1.0.0',
    description='Consume Bugzilla messages over STOMP and republish to Fedora Messaging',
    license='LGPLv2+',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/fedora-infra/bugzilla2fedmsg',
    # Possible options are at https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "fedora_messaging",
        "python-dateutil",
        "stompest",
        "pyasn1",
        "click",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": ["bugzilla2fedmsg=bugzilla2fedmsg:cli"],
        "fedora.messages": [
            "bugzilla2fedmsg.messageV1bz4=bugzilla2fedmsg_schema.schema:MessageV1BZ4",
            "bugzilla2fedmsg.messageV1=bugzilla2fedmsg_schema.schema:MessageV1",
        ],
    },
)
