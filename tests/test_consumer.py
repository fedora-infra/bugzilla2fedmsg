import pytest

from fedora_messaging.config import conf
from bugzilla2fedmsg.consumer import BugzillaConsumer
from stompest.error import StompConnectionError, StompProtocolError
from stompest.protocol import StompSpec
from stompest.protocol.frame import StompFrame


@pytest.fixture
def consumer(mocker):
    relay = mocker.Mock(name="relay")
    consumer = BugzillaConsumer(relay)
    # Stop after the first message
    relay.on_stomp_message.side_effect = lambda *args: consumer.stop()
    # Setup the transport
    transport = mocker.Mock(name="transport")
    transport.messages = []

    def _receive():
        frame = transport.messages.pop(0)
        if isinstance(frame, Exception):
            raise frame
        return frame

    transport.receive.side_effect = _receive
    transport_factory = mocker.Mock(name="transport_factory")
    transport_factory.return_value = transport
    consumer.stomp._transportFactory = transport_factory
    return consumer


@pytest.fixture
def connected_frame():
    return StompFrame(
        StompSpec.CONNECTED,
        {
            "server": "testing",
            "heart-beat": "1000,1000",
            "version": "1.2",
        },
    )


@pytest.fixture
def message_frame():
    return StompFrame(StompSpec.MESSAGE, {StompSpec.MESSAGE_ID_HEADER: "1312"}, b"true")


def test_connect(consumer, connected_frame, message_frame):
    transport_factory = consumer.stomp._transportFactory
    transport = transport_factory.return_value
    transport.messages.append(connected_frame)
    transport.messages.append(message_frame)
    consumer.consume()
    assert transport.connect.call_count == 1
    assert transport.send.call_count >= 3
    sent_frames = [call[0][0] for call in transport.send.call_args_list]
    assert sent_frames[0].command == StompSpec.CONNECT
    assert sent_frames[1].command == StompSpec.SUBSCRIBE
    assert sent_frames[1].headers["destination"] == "/queue/testing"
    assert sent_frames[2].command == StompSpec.ACK
    assert sent_frames[2].headers["message-id"] == "1312"


def test_connect_twice(consumer, connected_frame, message_frame):
    transport_factory = consumer.stomp._transportFactory
    transport = transport_factory.return_value
    transport.messages.append(connected_frame)
    transport.messages.append(StompConnectionError("test disconnect"))
    try:
        consumer.consume()
    except StompConnectionError:
        pass
    transport.messages.append(connected_frame)
    transport.messages.append(message_frame)
    try:
        consumer.consume()
    except StompConnectionError as e:
        assert False, "Must not fail when already connected: {}".format(e)
