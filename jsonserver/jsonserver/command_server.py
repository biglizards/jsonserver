import asyncio

from .server import BaseServer
from .utils import JSONReader


class CommandServer(BaseServer):
    """Adds commands and actual json. Read the full spec in the readme"""
    def __init__(self, command_field_name='command', reader_obj=JSONReader, **kwargs):
        super().__init__()
        self.commands = {}
        self.command_field_name = command_field_name
        self.reader_obj = reader_obj

        self.events['connect'] = self.default_on_connect
        self.events['message'] = self.handle_message

    def command(self, func):
        self.commands[func.__name__] = func
        return func

    async def default_on_connect(self, reader, writer):
        """Added to make it easier to swap out readers"""
        reader = self.reader_obj(reader)
        await self.handle_connection(reader, writer)

    async def handle_connection(self, reader, writer):
        """reads and dispatches new messages, and handling disconnects and errors"""
        while True:
            try:
                message = await reader.get_new_message()
                await self.dispatch('message', message, writer)
            except ConnectionError as e:
                await self.dispatch('disconnect', e)
                break
            except Exception as e:
                await self.dispatch('error', e)

    async def handle_message(self, message, writer):
        """for each message: get and dispatch the relevant command. {"command":"foo", "bar":5} calls foo()"""
        command = self.commands.get(message[self.command_field_name])
        if command is None:
            return  # ignore invalid command names

        result = command(message, writer)
        if asyncio.iscoroutine(result):
            return await result
        return result
