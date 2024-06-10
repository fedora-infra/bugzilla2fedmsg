""" STOMP consumer that listens to BZ and reproduces to Fedora Messaging.

Authors: Aurelien Bompard <abompard@fedoraproject.org>

"""

import json
import logging
import ssl
import threading

from stompest.config import StompConfig
from stompest.error import StompConnectionError, StompProtocolError
from stompest.protocol import StompSpec
from stompest.sync import Stomp


LOGGER = logging.getLogger(__name__)


class BugzillaConsumer:
    def __init__(self, conf, relay):
        self.relay = relay
        self._running = False
        self._heartbeat_timer = None
        self._conf = conf

        # Bugzilla
        self.products = self._conf.get("bugzilla", {}).get("products", ["Fedora", "Fedora EPEL"])

        # STOMP
        stomp_config = self._conf.get("stomp", {})
        self._queue_name = stomp_config.get("queue", "/queue/fedora_from_esb")
        self._heartbeat = stomp_config.get("heartbeat")
        self._vhost = stomp_config.get("vhost", "/")
        if stomp_config.get("ssl_crt") and stomp_config.get("ssl_key"):
            ssl_context = ssl.create_default_context()
            # Disable cert validation for demo only
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            ssl_context.load_cert_chain(stomp_config["ssl_crt"], stomp_config["ssl_key"])
        else:
            ssl_context = None

        stomp_config = StompConfig(
            stomp_config["uri"],
            login=stomp_config.get("user"),
            passcode=stomp_config.get("pass"),
            sslContext=ssl_context,
            version=StompSpec.VERSION_1_2,
        )
        self.stomp = Stomp(stomp_config)

        LOGGER.debug("Initialized bz2fm STOMP consumer.")

    def _connect(self):
        self._running = True
        LOGGER.debug("STOMP consumer is connecting...")
        heartbeats = None
        if self._heartbeat:
            heartbeats = (self._heartbeat, self._heartbeat)

        try:
            self.stomp.connect(host=self._vhost, heartBeats=heartbeats)
        except StompConnectionError as e:
            if e.args[0].startswith("Already connected to "):
                return
            raise

        self.setup_heartbeat()

        headers = {
            # client-individual mode is necessary for concurrent processing
            # (requires ActiveMQ >= 5.2)
            StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL
        }
        if self.stomp.session.version == StompSpec.VERSION_1_2:
            headers["id"] = 0
        try:
            self.stomp.subscribe(self._queue_name, headers)
        except StompProtocolError as e:
            if e.args[0].startswith("Already subscribed "):
                return
            raise

    def consume(self):
        self._connect()
        LOGGER.info("STOMP consumer is ready")
        while self._running:
            frame = self.stomp.receiveFrame()
            if frame.command != StompSpec.MESSAGE:
                continue
            body = json.loads(frame.body.decode())
            msg_id = frame.headers.get(StompSpec.MESSAGE_ID_HEADER)
            LOGGER.debug(f"Received message on STOMP with ID {msg_id}")
            try:
                self.relay.on_stomp_message(body, frame.headers)
            except Exception:
                LOGGER.exception("Exception when relaying the message:")
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
