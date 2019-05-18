import asyncio

from .command_server import CommandServer
from .utils import JSONWriter, Context, ArgumentError


class ExtendedServer(CommandServer):
    def __init__(self, *args, **kwargs):
        """various qol changes to the command server. Read the full spec in the readme
        
        Args:
            default_response (str, optional): sent when commands return None. Defaults to None (nothing is sent)
            command_field_name (str, optional): Name for the field containing the name of the command
                ie for command_field_name='foo', {"foo": "bar"} invokes bar()
            writer_obj (Object, optional): A wrapper for the asyncio stream writer implementing send_message
                Defaults to jsonServer.utils.JSONWriter
            reader_obj (Object, optional): A wrapper for the asyncio stream reader implementing get_message
                Defaults to jsonServer.utils.JSONReader
            context_obj (Object, optional): A factory for the context object.
            """
        super().__init__(*args, **kwargs)
        self.default_response = kwargs.get('default_response', None)
        self.writer_obj = kwargs.get('writer_obj', JSONWriter)
        self.context_obj = kwargs.get('context_obj', Context)
        self.connection_error = ConnectionError

    def command(self, func):
        if not asyncio.iscoroutinefunction(func):
            raise SyntaxError("ALL commands must be coroutines")
        self.commands[func.__name__] = func
        return func

    async def default_on_connect(self, reader, writer):
        writer = self.writer_obj(writer)
        reader = self.reader_obj(reader)
        await self.handle_connection(reader, writer)

    async def handle_connection(self, reader, writer):
        while True:
            ctx = self.context_obj(self, writer)  # for on_error/dc in case get_new_message fails
            try:
                message = await reader.get_new_message()
                print("MESSAGE:", message)
                ctx = self.context_obj(self, writer, message)
                await self.dispatch('message', ctx, message)
            except self.connection_error as e:
                await self.dispatch('disconnect', ctx, e)
                break
            except Exception as e:
                reply = await self.dispatch('error', ctx, e)
                if reply:
                    await writer.send_message(reply)

    async def handle_message(self, ctx, message):
        """similar to the command server, but with context and expands the arguments"""
        try:
            command = self.commands[message.pop(self.command_field_name)]
        except KeyError:
            return

        new_ctx = self.context_obj(self, ctx.writer, message, command)
        try:
            coro = command(new_ctx, **message)
        except (TypeError, ValueError):
            raise ArgumentError("invalid arguments")

        result = await coro
        if result is None:
            result = self.default_response

        await ctx.writer.send_message(result)
