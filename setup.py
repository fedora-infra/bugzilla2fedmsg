#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='bugzilla2fedmsg',
    version='0.4.0',
    description='Consume BZ messages over STOMP and republish to fedmsg',
    license='LGPLv2+',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/fedora-infra/bugzilla2fedmsg',
    install_requires=[
        "fedora_messaging",
        "python-dateutil",
        "stompest",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": ["bugzilla2fedmsg=bugzilla2fedmsg:cli"]
    },
)
