import json

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311


class Publisher:
    async def connect(self):
        raise NotImplementedError

    async def publish(self, type, apps):
        raise NotImplementedError


class StdoutPublisher(Publisher):
    async def connect(self):
        pass

    async def publish(self, type, apps):
        print(f"{type}: {apps}")


class MQTTPublisher(Publisher):
    def __init__(self, host, port, username, password):
        self._client = MQTTClient("call_watcher")
        self._client.set_auth_credentials(username, password)
        self._host = host
        self._port = port

    async def connect(self):
        await self._client.connect(
            self._host, port=self._port, ssl=True, version=MQTTv311
        )

    async def publish(self, type, apps):
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
