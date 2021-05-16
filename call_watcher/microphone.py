import asyncio
import logging

import pulsectl_asyncio

from .timer import timer


class Microphone:
    APP_NAME = "call_watcher"

    def __init__(self, queue):
        self._users = {}
        self._queue = queue

    async def run(self):
        async with pulsectl_asyncio.PulseAsync(self.APP_NAME) as pulse:
            await self._get_sources(pulse)
            await self._publish()
            asyncio.create_task(timer(self._publish, 60))

            async for event in pulse.subscribe_events("source_output"):
                if event.t not in ["new", "remove"]:
                    continue

                if event.t == "new":
                    source = await pulse.source_output_info(event.index)
                    self._users[event.index] = source.proplist["application.name"]

                if event.t == "remove":
                    source = self._users[event.index]
                    del self._users[event.index]

                await self._publish()

    async def _publish(self):
        await self._queue.put(
            {
                "type": "microphone",
                "apps": list(self._users.values()),
            }
        )

    async def _get_sources(self, pulse):
        sources = await pulse.source_output_list()
        for source in sources:
            self._users[source.index] = source.proplist["application.name"]
