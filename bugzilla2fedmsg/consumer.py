"""Kafka consumer that listens to BZ and reproduces to Fedora Messaging.

Authors: Aurelien Bompard <abompard@fedoraproject.org>

"""

import json
import logging

from fedora_messaging.config import conf as fm_config
from kafka import KafkaConsumer

LOGGER = logging.getLogger(__name__)


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
            body = json.loads(message.value.decode("utf-8"))
            LOGGER.debug(
                f"Received message from Kafka on topic {message.topic}, "
                f"partition {message.partition}, offset {message.offset} "
                f"with key {message.key.decode('ascii')}"
            )
            try:
                self.relay.on_kafka_message(body)
            except Exception:
                LOGGER.exception("Exception when relaying the message:")

    def stop(self):
        if hasattr(self, "_kafka") and self._kafka:
            self._kafka.close()
