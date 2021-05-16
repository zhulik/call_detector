import asyncio
import logging
import os
import signal
import sys
from contextlib import suppress

from call_watcher.camera import Camera
from call_watcher.microphone import Microphone
from call_watcher.publishers import MQTTPublisher


async def report_mic_users():
    audio = Microphone()
    async for users in audio.users():
        await publisher.publish("microphone", users)


async def report_cam_users():
    video = Camera()
    async for users in video.users():
        await publisher.publish("camera", users)


async def main():
    host = os.environ["MQTT_HOST"]
    port = int(os.environ.get("MQTT_PORT", 8883))
    username = os.environ["MQTT_USERNAME"]
    password = os.environ["MQTT_PASSWORD"]

    queue = asyncio.Queue()

    microphone = Microphone(queue)
    camera = Camera(queue)
    publisher = MQTTPublisher(host, port, username, password, queue)

    mic_users_task = asyncio.create_task(microphone.run())
    cam_users_task = asyncio.create_task(camera.run())
    publisher_task = asyncio.create_task(publisher.run())

    await asyncio.wait([cam_users_task, mic_users_task, publisher_task])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
