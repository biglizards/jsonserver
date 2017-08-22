import asyncio
import functools

from .utils import remove_leading_on


class BaseServer:
    """A basic wrapper around the asyncio streams library. Doesnt have anything to do with json at this level"""
    def __init__(self):
        self.events = {}

    def event(self, func):
        """wrapper for events, adds them to a dictionary to be dispatched later"""
        name = remove_leading_on(func.__name__)
        self.events[name] = func
        return func

    async def dispatch(self, name, *args, **kwargs):
        """runs self.events[name], passing all additional arguments, awaiting if needed"""
        try:
            event = self.events[name]
        except KeyError:
            return None

        if asyncio.iscoroutinefunction(event):
            return await event(*args, **kwargs)
        else:
            return event(*args, **kwargs)

    def run(self, addr='127.0.0.1', port=8888, loop=None):
        """starts the asyncio server, dispatching on_connect when needed"""
        if loop is None:
            loop = asyncio.get_event_loop()

        callback = functools.partial(self.dispatch, 'connect')
        coro = asyncio.start_server(callback, addr, port, loop=loop)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        # cleanup, just to be safe
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


