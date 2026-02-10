import logging
import os

import click
from fedora_messaging.config import conf as fm_config
from fedora_messaging.exceptions import ConfigurationException

from bugzilla2fedmsg.consumer import BugzillaConsumer
from bugzilla2fedmsg.relay import MessageRelay

LOGGER = logging.getLogger(__name__)


@click.command()
@click.option("-c", "--config", envvar="FEDORA_MESSAGING_CONF", help="Configuration file")
def cli(config):
    """Relay Bugzilla changes into Fedora Messaging."""
    if config:
        if not os.path.isfile(config):
            raise click.exceptions.BadParameter(f"{config} is not a file")
        try:
            fm_config.load_config(config_path=config)
        except ConfigurationException as e:
            raise click.exceptions.BadParameter(str(e)) from e
    fm_config.setup_logging()

    # Now start the consumer.
    conf = fm_config["consumer_config"]
    relay = MessageRelay(conf)
    consumer = BugzillaConsumer(conf, relay)
    try:
        consumer.consume()
    except KeyboardInterrupt:
        consumer.stop()
        raise
