import logging
import os
import time
import logging

import click
import fedora_messaging
from stompest.error import StompConnectionError

from bugzilla2fedmsg.consumer import BugzillaConsumer
from bugzilla2fedmsg.relay import MessageRelay


LOGGER = logging.getLogger(__name__)


@click.command()
@click.option(
    "-c", "--config", envvar="FEDORA_MESSAGING_CONF", help="Configuration file"
)
def cli(config):
    """Relay Bugzilla changes into Fedora Messaging."""
    if config:
        if not os.path.isfile(config):
            raise click.exceptions.BadParameter("{} is not a file".format(config))
        try:
            fedora_messaging.config.conf.load_config(config_path=config)
        except fedora_messaging.exceptions.ConfigurationException as e:
            raise click.exceptions.BadParameter(str(e))
    fedora_messaging.config.conf.setup_logging()

    # Now start the consumer.
    conf = fedora_messaging.config.conf["consumer_config"]
    relay = MessageRelay(conf)
    consumer = BugzillaConsumer(conf, relay)
    while True:
        try:
            consumer.consume()
        except StompConnectionError:
            LOGGER.exception("Disconnected: ")
            time.sleep(3)
        except KeyboardInterrupt:
            consumer.stop()
            raise
