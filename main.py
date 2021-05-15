import asyncio
import logging
import signal
import sys
from contextlib import suppress

from media_devices.audio import Audio
from media_devices.video import Video


async def report_mic_users():
    audio = Audio()
    async for users in audio.users():
        print("Audio:", users)


async def report_cam_users():
    video = Video()
    async for users in video.users():
        print("Camera:", users)


async def main():
    mic_users_task = asyncio.create_task(report_mic_users())
    cam_users_task = asyncio.create_task(report_cam_users())

    await asyncio.wait([cam_users_task, mic_users_task])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
