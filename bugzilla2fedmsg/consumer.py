"""Kafka consumer that listens to BZ and reproduces to Fedora Messaging.

Authors: Aurelien Bompard <abompard@fedoraproject.org>

"""

import json
import logging

from fedora_messaging.config import conf as fm_config
from kafka import KafkaConsumer
from kafka.errors import CommitFailedError

LOGGER = logging.getLogger(__name__)

# Relaying a message can be slow: it does an HTTP request to FASJSON for every email
# address involved, and then publishes to RabbitMQ. With the default settings, Kafka
# would hand us batches of 500 records and only commit the offsets when we ask for the
# next batch, so a crash or a rebalance in the meantime would make the broker send us
# the whole batch again. Instead, ask for small batches and commit after each message.
KAFKA_OPTIONS = {
    "enable_auto_commit": False,
    "max_poll_records": 10,
}


class BugzillaConsumer:
    _kafka_consumer_class = KafkaConsumer

    def __init__(self, conf, relay):
        self.relay = relay
        self._conf = conf

        # Bugzilla
        self.products = self._conf.get("bugzilla", {}).get("products", ["Fedora", "Fedora EPEL"])

        # Kafka
        self._kafka: KafkaConsumer

    def _connect(self):
        kwargs = dict(
            group_id=fm_config["client_properties"]["app"],
            bootstrap_servers=self._conf["kafka"]["servers"],
            **KAFKA_OPTIONS,
        )
        if self._conf["kafka"].get("username") and self._conf["kafka"].get("password"):
            kwargs.update(
                dict(
                    security_protocol="SASL_SSL",
                    sasl_mechanism="SCRAM-SHA-512",
                    sasl_plain_username=self._conf["kafka"]["username"],
                    sasl_plain_password=self._conf["kafka"]["password"],
                )
            )
        self._kafka = self._kafka_consumer_class(*self._conf["kafka"]["topics"], **kwargs)
        LOGGER.debug("Initialized Kafka consumer.")

    def consume(self):
        self._connect()
        LOGGER.info("Kafka consumer is ready")
        for message in self._kafka:
            self._handle_message(message)
            # This is at-least-once delivery: committing after the message has been
            # relayed means we may relay it twice if we're interrupted right now, but
            # the window is a single message instead of a whole batch.
            try:
                self._kafka.commit()
            except CommitFailedError as e:
                # The group has rebalanced and the partition is somebody else's problem
                # now, they will relay the message again.
                LOGGER.warning(f"Could not commit the offset: {e}")

    def _handle_message(self, message):
        LOGGER.debug(
            "Received message from Kafka on topic %s, partition %s, offset %s with key %r",
            message.topic,
            message.partition,
            message.offset,
            message.key,
        )
        try:
            body = json.loads(message.value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Don't let an unparsable message kill the process: we would just read it
            # again on restart, and again, and again.
            LOGGER.exception("Could not decode the message, dropping it:")
            return
        try:
            self.relay.on_kafka_message(body)
        except Exception:
            LOGGER.exception("Exception when relaying the message:")

    def stop(self):
        if hasattr(self, "_kafka") and self._kafka:
            self._kafka.close()
