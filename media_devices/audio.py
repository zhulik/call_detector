import logging

import pulsectl_asyncio

_LOGGER = logging.getLogger(__name__)


class Audio:
    APP_NAME = "event-listener"

    def __init__(self):
        self.sources = {}

    async def listen(self):
        async with pulsectl_asyncio.PulseAsync(self.APP_NAME) as pulse:
            await self._get_sources(pulse)
            async for event in pulse.subscribe_events("source_output"):
                if event.t not in ["new", "remove"]:
                    continue

                if event.t == "new":
                    source = await pulse.source_output_info(event.index)
                    self.sources[event.index] = source
                    _LOGGER.debug(
                        "Started listening: %s", source.proplist["application.name"]
                    )

                if event.t == "remove":
                    source = self.sources[event.index]
                    del self.sources[event.index]
                    _LOGGER.debug(
                        "Stopped listening: %s", source.proplist["application.name"]
                    )

    async def _get_sources(self, pulse):
        sources = await pulse.source_output_list()
        for source in sources:
            self.sources[source.index] = source
