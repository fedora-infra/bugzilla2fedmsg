import json

import pytest
from kafka.consumer.fetcher import ConsumerRecord

from bugzilla2fedmsg.consumer import BugzillaConsumer


@pytest.fixture
def consumer_config():
    return {
        "fasjson_url": "https://fasjson.example.com",
        "kafka": {
            "servers": ["localhost:9096"],
            "username": "username",
            "password": "password",
            "topics": ["dev.ants.engineering.bugzilla.bug"],
        },
        "bugzilla": {
            "products": ["Fedora", "Fedora EPEL"],
            "bz4compat": True,
        },
    }


@pytest.fixture
def consumer(mocker, consumer_config):
    relay = mocker.Mock(name="relay")
    kafka_consumer = mocker.Mock(name="kafka_consumer")

    mocker.patch.object(BugzillaConsumer, "_kafka_consumer_class", return_value=kafka_consumer)
    consumer = BugzillaConsumer(consumer_config, relay)
    consumer.test_messages = []
    kafka_consumer.__iter__ = mocker.Mock(return_value=iter(consumer.test_messages))
    kafka_consumer.__next__ = mocker.Mock(side_effect=lambda: next(consumer.test_messages))
    return consumer


def make_record(value):
    encoded_value = json.dumps(value).encode("utf-8")
    return ConsumerRecord(
        topic="dummy.topic",
        key=b"dummy.key",
        value=encoded_value,
        partition=1,
        offset=1,
        leader_epoch=0,
        timestamp=1,
        timestamp_type=0,
        headers=[],
        checksum=0,
        serialized_header_size=-1,
        serialized_key_size=1,
        serialized_value_size=len(encoded_value),
    )


def test_connect_consume(consumer):
    dummy_message = {"dummy": "message"}
    consumer.test_messages.append(make_record(dummy_message))
    consumer.consume()
    consumer._kafka_consumer_class.assert_called_once_with(
        "dev.ants.engineering.bugzilla.bug",
        bootstrap_servers=["localhost:9096"],
        group_id="Example Application",
        sasl_mechanism="SCRAM-SHA-512",
        sasl_plain_password="password",  # noqa: S106
        sasl_plain_username="username",
        security_protocol="SASL_SSL",
    )
    consumer.relay.on_kafka_message.assert_called_once_with(dummy_message)


def test_connect_consume_relaying_failed(consumer, caplog):
    dummy_message = {"dummy": "message"}
    consumer.test_messages.append(make_record(dummy_message))
    consumer.relay.on_kafka_message.side_effect = ValueError("dummy error")
    consumer.consume()
    consumer.relay.on_kafka_message.assert_called_once()
    assert caplog.messages == ["Exception when relaying the message:"]
    assert caplog.records[0].levelname == "ERROR"


def test_close(consumer):
    consumer.consume()
    consumer.stop()
    consumer._kafka.close.assert_called_once_with()


def test_close_before_consume(consumer):
    consumer.stop()
    assert not hasattr(consumer, "_kafka")
