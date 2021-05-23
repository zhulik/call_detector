import asyncio
import json
import logging
import socket
from functools import reduce

import async_timeout
from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311

from . import UPDATE_INTERVAL


def throttle(seconds):
    class Throttler:
        def __init__(self, seconds, func):
            self._seconds = seconds
            self._func = func
            self._task = None

        async def func(self, obj):
            if self._task is None:
                self._task = asyncio.create_task(self._delayed_call(obj))

        async def _delayed_call(self, obj):
            await asyncio.sleep(self._seconds)
            await self._func(obj)
            self._task = None

    def decorator(func):
        throttler = Throttler(seconds, func)
        return lambda obj: throttler.func(obj)  # pylint: disable=unnecessary-lambda

    return decorator


class MQTTPublisher:  # pylint: disable=too-many-instance-attributes
    _LOGGER = logging.getLogger(f"{__name__}.{__qualname__}")

    def __init__(  # pylint: disable=too-many-arguments
        self,
        queue,
        host="localhost",
        port=8333,
        username=None,
        password=None,
        ssl=False,
        retry=False,
        topic=f"call_detector/{socket.gethostname()}",
    ):
        self._client = MQTTClient("call_detector")
        if username is not None:
            self._client.set_auth_credentials(username, password)

        self._host = host
        self._port = port
        self._queue = queue
        self._topic = topic
        self._retry = retry
        self._ssl = ssl

        self._state = {"call": False}

    async def run(self):
        self._LOGGER.info("Running.")

        await self._client.connect(self._host, port=self._port, ssl=self._ssl, version=MQTTv311, keepalive=10)
        self._LOGGER.info("Connected.")

        while True:
            try:
                try:
                    with async_timeout.timeout(UPDATE_INTERVAL):
                        msg = await self._queue.get()
                        self._update_state(msg)
                except asyncio.exceptions.TimeoutError:
                    pass

                await self._publish_state()
            except Exception:  # pylint: disable=broad-except
                if not self._retry:
                    raise
                self._LOGGER.exception("Error occured during timer execution")
                await asyncio.sleep(5)

    def _update_state(self, msg):
        del self._state["call"]
        self._state[msg["source"]] = msg["apps"]

        apps = reduce(lambda a, b: a + len(b), self._state.values(), 0)
        self._state["call"] = apps > 0

        self._LOGGER.info("State updated: %s", self._state)

    @throttle(0.5)
    async def _publish_state(self):
        self._LOGGER.info("Publishing state %s to topic %s", self._state, self._topic)
        self._client.publish(
            self._topic,
            json.dumps(self._state),
            qos=1,
        )
