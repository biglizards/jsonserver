import asyncio

from .extended_server import ExtendedServer


class Client(ExtendedServer):
    def run(self, addr='127.0.0.1', port=8888, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        loop.run_until_complete(self._connect(addr, port, loop))

    async def _connect(self, addr, port, loop):
        reader, writer = await asyncio.open_connection(addr, port, loop=loop)
        await self.dispatch('connect', reader, writer)


