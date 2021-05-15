import logging

import pulsectl_asyncio


class Microphone:
    APP_NAME = "event-listener"

    def __init__(self):
        self._users = {}

    async def users(self):
        async with pulsectl_asyncio.PulseAsync(self.APP_NAME) as pulse:
            await self._get_sources(pulse)
            async for event in pulse.subscribe_events("source_output"):
                if event.t not in ["new", "remove"]:
                    continue

                if event.t == "new":
                    source = await pulse.source_output_info(event.index)
                    self._users[event.index] = source.proplist["application.name"]

                if event.t == "remove":
                    source = self._users[event.index]
                    del self._users[event.index]
                yield list(self._users.values())

    async def _get_sources(self, pulse):
        sources = await pulse.source_output_list()
        for source in sources:
            self._users[source.index] = source.proplist["application.name"]
