import asyncio
import logging
import signal
import sys
from contextlib import suppress

from media_devices.audio import Audio


def setup_logger():
  root = logging.getLogger()
  root.setLevel(logging.DEBUG)
  
  handler = logging.StreamHandler(sys.stdout)
  handler.setLevel(logging.DEBUG)
  fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  handler.setFormatter(fmt)
  root.addHandler(handler)

async def main():
    setup_logger()

    audio = Audio()
    listen_task = asyncio.create_task(audio.listen())

    # register signal handlers to cancel listener when program is asked to terminate
    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        loop.add_signal_handler(sig, listen_task.cancel)
    # Alternatively, the PulseAudio event subscription can be ended by breaking/returning from the `async for` loop

    with suppress(asyncio.CancelledError):
        await listen_task

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())