import json
import traceback

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311


class Publisher:
    async def publish(self, type, apps):
        raise NotImplementedError


class StdoutPublisher(Publisher):
    async def publish(self, type, apps):
        print(f"{type}: {apps}")


class MQTTPublisher(Publisher):
    def __init__(self, host, port, username, password):
        self._client = MQTTClient("call_watcher")
        self._client.set_auth_credentials(username, password)
        self._host = host
        self._port = port
        self._connected = False

    async def publish(self, type, apps):
        try:
            await self._connect()

            self._client.publish(
                f"call_watcher/{type}",
                json.dumps(
                    {
                        "count": len(apps),
                        "apps": apps,
                    }
                ),
                qos=1,
            )
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            self._connected = False

    async def _connect(self):
        if self._connected:
            return

        await self._client.connect(
            self._host, port=self._port, ssl=True, version=MQTTv311
        )
        self._connected = True
