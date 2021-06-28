import logging
from copy import deepcopy

import pulsectl_asyncio


class Microphone:
    APP_NAME = "call_detector"

    IGNORED_APPS = ["plasmashell"]

    _LOGGER = logging.getLogger(f"{__name__}.{__qualname__}")

    def __init__(self, queue):
        self._users = {}
        self._queue = queue

    async def run(self):
        self._LOGGER.info("Running.")

        async with pulsectl_asyncio.PulseAsync(self.APP_NAME) as pulse:
            await self._get_sources(pulse)
            await self._publish()

            async for event in pulse.subscribe_events("source_output"):
                if event.t not in ["new", "remove"]:
                    continue

                if event.t == "new":
                    source = await pulse.source_output_info(event.index)
                    self._users[event.index] = source.proplist["application.process.binary"]

                if event.t == "remove":
                    source = self._users[event.index]
                    del self._users[event.index]

                await self._publish()

    async def _publish(self):
        await self._queue.put(
            {
                "source": "microphone",
                "apps": self._apps_to_publish(),
            }
        )

    async def _get_sources(self, pulse):
        sources = await pulse.source_output_list()
        for source in sources:
            self._users[source.index] = source.proplist["application.process.binary"]

    def _apps_to_publish(self):
        apps = list(set(deepcopy(list(self._users.values()))))
        for app in self.IGNORED_APPS:
            if app in apps:
                apps.remove(app)
        return apps
