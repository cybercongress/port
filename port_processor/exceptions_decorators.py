import asyncio
import functools
import logging
import concurrent.futures


from websockets.exceptions import WebSocketException
from aiohttp import ClientError, ClientResponseError, ClientConnectionError, ClientPayloadError, ServerTimeoutError, ServerDisconnectedError
from socket import error
from config import TIME_SLEEP


client_exceptions = (
    ClientError,
    ClientResponseError,
    ClientConnectionError,
    ClientPayloadError,
    ServerTimeoutError,
    concurrent.futures.CancelledError,
    ServerDisconnectedError,
    OSError
)



logging.basicConfig(format='%(asctime)s %(message)s')

def ws_exception_handler(f):
    @functools.wraps(f)
    async def wrapped(*args, **kwargs):
        while True:
            try:
                return await f(*args, **kwargs)
            except (WebSocketException, error) as e:
                logging.warning(f"WS exception handled in {f.__name__}\n{e}\nWaiting for {TIME_SLEEP} seconds and trying again")
                await asyncio.sleep(TIME_SLEEP)
    return wrapped


def aiohttp_exception_handler(f):
    @functools.wraps(f)
    async def wrapped(*args, **kwargs):
        while True:
            try:
                return await f(*args, **kwargs)
            except client_exceptions as e:
                logging.warning(f"aiohttp exception handled in {f.__name__}\n{e!r}\nWaiting for {TIME_SLEEP} seconds and trying again")
                await asyncio.sleep(TIME_SLEEP)
    return wrapped



