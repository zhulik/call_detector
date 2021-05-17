import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


async def timer(func, sleep_time):
    while True:
        try:
            await func()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Error occured during timer execution")
        finally:
            await asyncio.sleep(sleep_time)
