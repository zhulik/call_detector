import asyncio
import logging
import os
import sys

from call_watcher.camera import Camera
from call_watcher.microphone import Microphone
from call_watcher.publishers import MQTTPublisher


def setup_logger(level):
    root = logging.getLogger("call_watcher")
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(fmt)
    root.addHandler(handler)


async def main():
    host = os.environ.get("MQTT_HOST", "localhost")
    port = int(os.environ.get("MQTT_PORT", 8883))
    username = os.environ.get("MQTT_USERNAME", None)
    password = os.environ.get("MQTT_PASSWORD", None)

    setup_logger(logging.DEBUG)

    queue = asyncio.Queue()

    microphone = Microphone(queue)
    camera = Camera(queue)
    publisher = MQTTPublisher(
        host=host,
        port=port,
        username=username,
        password=password,
        ssl=True,
        queue=queue,
    )

    await asyncio.gather(microphone.run(), camera.run(), publisher.run())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
