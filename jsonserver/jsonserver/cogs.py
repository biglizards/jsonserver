import importlib
import inspect


class Command:
    def __init__(self, func):
        self.func = func


class Event:
    def __init__(self, func):
        self.func = func


def load_cogs(cogs, server):
    """given a list of cogs, imports them and adds any commands or events to the correct dict
    
    note that some events (only on_connect iirc) cannot be passed a reference to the server because of the way asycio
    works, but why would you want your on_connect in a different file anyway
    Plus you can just subclass the server and get a reference from the `self` param
    """
    for cog in cogs:
        cog_module = importlib.import_module(cog)
        commands = inspect.getmembers(cog_module, lambda f: isinstance(f, Command))
        events = inspect.getmembers(cog_module, lambda f: isinstance(f, Event))

        server.commands.update((name, command.func) for name, command in commands)
        server.events.update((name, event.func) for name, event in events)
