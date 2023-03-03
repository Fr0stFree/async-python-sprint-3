import asyncio
import logging.config
import threading

from aioconsole import ainput

from server.core.network import DataTransport, Request, Update
from settings import Settings
from utils.functions import print_update
from gui.chat import ChatApp


settings = Settings()
# logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, server_host: str, server_port: int) -> None:
        self._server_host = server_host
        self._server_port = server_port
        self._transport: DataTransport | None = None
        self._request_queue: asyncio.Queue = asyncio.Queue()
        self._receiver: asyncio.Task | None = None

    async def __aenter__(self) -> 'Client':
        reader, writer = await asyncio.open_connection(self._server_host, self._server_port)
        self._transport = DataTransport(writer, reader)
        logger.debug("Connected to %s:%s", self._server_host, self._server_port)
        self._receiver = asyncio.ensure_future(self._receive_data())
        self._sender = asyncio.ensure_future(self._send_data())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._request_queue.join()
        self._receiver.cancel()
        await self._transport.close()
        logger.info("Connection to %s:%s is closed", self._server_host, self._server_port)

    async def _receive_data(self) -> None:
        while True:
            try:
                data = await self._transport.receive()
                update = Update.from_json(data)
                print_update(update)
            except ConnectionError:
                break

    async def _send_data(self) -> None:
        while True:
            statement = await self._request_queue.get()
            command, *value = statement.split()
            request = Request(command, ' '.join(value))
            await self._transport.transfer(request.to_json())

    @property
    def request_queue(self) -> asyncio.Queue:
        return self._request_queue


    async def handle_input(self) -> None:
        while True:
            statement = await ainput()
            match statement.split():
                case [command, *value]:
                    await self._request_queue.put(statement)
                    if command == 'exit':
                        break
                case _:
                    continue


async def main():
    async with Client(server_host=settings.SERVER_HOST, server_port=settings.SERVER_PORT) as client:
        await ChatApp(requests=client.request_queue).async_run(async_lib='asyncio')


if __name__ == '__main__':
   asyncio.run(main())



