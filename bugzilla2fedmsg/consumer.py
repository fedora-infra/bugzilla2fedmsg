""" STOMP consumer that listens to BZ and reproduces to Fedora Messaging.

Authors: Aurelien Bompard <abompard@fedoraproject.org>

"""

import json
import logging
import ssl
import threading

from fedora_messaging.config import conf
from stompest.config import StompConfig
from stompest.protocol import StompSpec
from stompest.sync import Stomp


LOGGER = logging.getLogger(__name__)


class BugzillaConsumer:
    def __init__(self, relay):
        self.relay = relay
        self._running = False
        self._heartbeat_timer = None

        # Bugzilla
        self.products = (
            conf["consumer_config"]
            .get("bugzilla", {})
            .get("products", ["Fedora", "Fedora EPEL"])
        )

        # STOMP
        stomp_config = conf["consumer_config"].get("stomp", {})
        self._queue_name = stomp_config.get("queue", "/queue/fedora_from_esb")
        self._heartbeat = stomp_config.get("heartbeat")
        ssl_context = ssl.create_default_context()
        # Disable cert validation for demo only
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.load_cert_chain(stomp_config["ssl_crt"], stomp_config["ssl_key"])

        stomp_config = StompConfig(
            stomp_config["uri"],
            login=stomp_config.get("user"),
            passcode=stomp_config.get("pass"),
            sslContext=ssl_context,
            version=StompSpec.VERSION_1_2,
        )
        self.stomp = Stomp(stomp_config)

        LOGGER.debug("Initialized bz2fm STOMP consumer.")

    def consume(self):
        self._running = True
        LOGGER.debug("STOMP consumer is connecting...")
        heartbeats = None
        if self._heartbeat:
            heartbeats = (self._heartbeat, self._heartbeat)
        self.stomp.connect(heartBeats=heartbeats)
        headers = {
            # client-individual mode is necessary for concurrent processing
            # (requires ActiveMQ >= 5.2)
            StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL
        }
        if self.stomp.session.version == StompSpec.VERSION_1_2:
            headers["id"] = 0
        self.setup_heartbeat()
        self.stomp.subscribe(self._queue_name, headers)
        LOGGER.info("STOMP consumer is ready")
        while self._running:
            frame = self.stomp.receiveFrame()
            if frame.command != StompSpec.MESSAGE:
                continue
            body = json.loads(frame.body.decode())
            msg_id = frame.headers.get(StompSpec.MESSAGE_ID_HEADER)
            LOGGER.debug("Received message on STOMP with ID {}".format(msg_id))
            try:
                self.relay.on_stomp_message(body, frame.headers)
            except Exception:
                self.stomp.nack(frame)
            else:
                self.stomp.ack(frame)
        self.stomp.disconnect()

    def stop(self):
        self._running = False
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()

    def setup_heartbeat(self):
        if not self._heartbeat:
            return

        def _send_heartbeat():
            if not self._running:
                return
            self.stomp.beat()
            self.setup_heartbeat()
        delay = self._heartbeat - self._heartbeat / 10
        self._heartbeat_timer = threading.Timer(delay / 1000, _send_heartbeat)
        self._heartbeat_timer.start()
