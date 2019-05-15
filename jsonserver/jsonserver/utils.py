import json
from numbers import Number

import struct


class ArgumentError(Exception):
    pass


class JSONDecodeError(ValueError):
    pass


def remove_leading_on(name):
    if name.startswith('on_'):
        return name[3:]
    return name


class Context:
    """Storage for various bits of contextual information. Should probably just be a named tuple"""
    def __init__(self, server, writer, message=None, command=None):
        self.server = server

        self.writer = writer
        self.send = self.writer.send_message

        self.message = message
        self.command = command


class JSONWriter:
    def __init__(self, writer):
        self._writer = writer

    async def send_message(self, message):
        """encode the message, first sending its size (two bytes), then the real message"""
        if message is None:
            return
        if isinstance(message, dict):
            message = json.dumps(message)
        if isinstance(message, Number):
            message = str(message)
        if isinstance(message, str):
            message = message.encode()

        size = struct.pack('>H', len(message))
        data = size + message
        self._writer.write(data)


class JSONReader:
    def __init__(self, reader):
        self.reader = reader

    async def read(self, n=-1):
        """read n bytes. If b'' (client disconnected) raise an error"""
        data = await self.reader.read(n)
        if data is b'':
            raise ConnectionError("client disconnected")
            # this is so it can be caught and on_disconnect dispatched during get_new_message
            # which has multiple reads
        return data

    async def get_new_message(self):
        """read two bytes, containing the length of the message. read that many bytes, returning the decoded json"""
        raw_size = await self.read(2)
        size = struct.unpack('>H', raw_size)[0]

        data = await self.read(size)
        try:
            return json.loads(data)
        except ValueError as e:
            raise JSONDecodeError(e, data)
