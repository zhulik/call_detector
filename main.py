import asyncio
import logging
import signal
import sys
from contextlib import suppress

from media_devices.audio import Audio
from media_devices.video import Video


def setup_logger():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(fmt)
    root.addHandler(handler)


async def report_mic_users():
    audio = Audio()
    async for users in audio.users():
        print(users)


async def report_cam_users():
    video = Video()
    async for users in video.users():
        print(users)


async def main():
    setup_logger()

    mic_users_task = asyncio.create_task(report_mic_users())
    cam_users_task = asyncio.create_task(report_cam_users())

    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        loop.add_signal_handler(sig, mic_users_task.cancel)
        loop.add_signal_handler(sig, cam_users_task.cancel)

    with suppress(asyncio.CancelledError):
        await cam_users_task
        await mic_users_task


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
