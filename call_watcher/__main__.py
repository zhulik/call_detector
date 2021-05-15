import asyncio
import logging
import signal
import sys
import os
from contextlib import suppress

from call_watcher.camera import Camera
from call_watcher.microphone import Microphone
from call_watcher.publishers import MQTTPublisher


async def report_mic_users(publisher):
    audio = Microphone()
    async for users in audio.users():
        await publisher.publish("microphone", users)


async def report_cam_users(publisher):
    video = Camera()
    async for users in video.users():
        await publisher.publish("camera", users)


async def main():
    host = os.environ["MQTT_HOST"]
    port = int(os.environ.get("MQTT_PORT", 8883))
    username = os.environ["MQTT_USERNAME"]
    password = os.environ["MQTT_PASSWORD"]
    publisher = MQTTPublisher(host, port, username, password)
    await publisher.connect()
    mic_users_task = asyncio.create_task(report_mic_users(publisher))
    cam_users_task = asyncio.create_task(report_cam_users(publisher))

    await asyncio.wait([cam_users_task, mic_users_task])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
