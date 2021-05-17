import asyncio
import json
import logging
import socket

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311

_LOGGER = logging.getLogger(__name__)


class MQTTPublisher:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        queue,
        host="localhost",
        port=8333,
        username=None,
        password=None,
        topic=f"call_watcher/{socket.gethostname()}",
    ):
        self._client = MQTTClient("call_watcher")
        self._client.set_auth_credentials(username, password)
        self._host = host
        self._port = port
        self._queue = queue
        self._topic = topic

        self._connected = False

    async def run(self):
        _LOGGER.info("Running.")

        while True:
            try:
                msg = await self._queue.get()
                await self._connect()

                self._client.publish(
                    f"{self._topic}/{msg['source']}",
                    json.dumps(msg["data"]),
                    qos=1,
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Error occured during timer execution")
                self._connected = False
                await asyncio.sleep(5)

    async def _connect(self):
        if self._connected:
            return

        await self._client.connect(self._host, port=self._port, ssl=True, version=MQTTv311)
        self._connected = True