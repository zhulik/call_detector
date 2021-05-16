import asyncio
import glob
import os
from copy import deepcopy
from dataclasses import dataclass
from os.path import join
from pathlib import Path

from minotaur import Inotify, Mask

from .timer import timer

PROC_PATH = "/proc"


def lsof(filename):
    pids = [int(name) for name in os.listdir(PROC_PATH) if name.isnumeric()]
    result = set()
    for pid in pids:
        try:
            p_path = join(PROC_PATH, str(pid))
            fd_path = join(p_path, "fd")
            fds = os.listdir(fd_path)
            for fd in fds:
                if os.readlink(join(fd_path, fd)) == filename:
                    p_name = join(p_path, "comm")
                    name = Path(p_name).read_text().rstrip()
                    result.add(name)
        except (PermissionError, FileNotFoundError):
            continue
    return list(result)


async def camera_users():
    result = []
    for filename in glob.glob("/dev/video*"):
        result += lsof(filename)
    return list(set(result))


class Camera:
    def __init__(self, queue):
        self._users = []
        self._queue = queue

    async def run(self):
        self._users = await camera_users()
        await self._publish()
        self._cameras = glob.glob("/dev/video*")
        asyncio.create_task(timer(self._publish, 60))

        with Inotify(blocking=False) as inotify:
            for camera in self._cameras:
                inotify.add_watch(camera, Mask.OPEN | Mask.CLOSE)

            async for event in inotify:
                users = await camera_users()
                if users != self._users:
                    self._users = users
                    await self._publish()

    async def _publish(self):
        await self._queue.put(
            {
                "type": "camera",
                "apps": deepcopy(self._users),
            }
        )
