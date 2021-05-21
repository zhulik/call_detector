import asyncio
import getpass
import logging
import sys
import socket

import click

from .camera import Camera
from .microphone import Microphone
from .publishers import MQTTPublisher


def setup_logger(level):
    root = logging.getLogger("call_detector")
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(fmt)
    root.addHandler(handler)


@click.command(context_settings={"max_content_width": 120, "show_default": True})
@click.option("-H", "--host", default="localhost", help="Host")
@click.option("-U", "--username", help="Username")
@click.option("-P", "--password", help="Password")
@click.option("-p", "--port", default=8883, help="Port")
@click.option("-t", "--topic", default=f"call_detector/{socket.gethostname()}", help="MQTT Topic")
@click.option("-s", "--ssl", is_flag=True, default=True, help="Use SSL")
@click.option("-a", "--ask-password", is_flag=True, help="Read password from stdin")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("-r", "--retry/--no-retry", is_flag=True, default=False, help="Keep retrying if can't connect")
def main(
    host, username, password, port, ssl, retry, ask_password, verbose, topic
):  # pylint: disable=too-many-arguments
    if verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING

    setup_logger(loglevel)

    queue = asyncio.Queue()

    if ask_password:
        password = getpass.getpass()

    microphone = Microphone(queue)
    camera = Camera(queue)
    publisher = MQTTPublisher(
        host=host,
        port=port,
        username=username,
        password=password,
        ssl=ssl,
        queue=queue,
        retry=retry,
        topic=topic,
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(microphone.run(), camera.run(), publisher.run()))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
