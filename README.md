# jsonserver
A discord.py inspired wrapper for the asyncio streams library using JSON

### Examples

The extended server (honestly it should just be the default) is the highest level server, and typically the easiest to use.

```py
import jsonServer
server = jsonServer.ExtendedServer(addr='127.0.0.1', port=8888)

# set up a command -- when json like {"command": "add", "a": 1, "b": 2} is received, it calls
# the appropriate command with the other arguments.
@server.command
async def add(ctx, a, b):
    # the return value of the function is sent back automatically, though not wrapped in any JSON by default
    return a + b

server.run()
```

You could also use the CommandServer, although I have no idea why you would want to:

```py
server = jsonServer.CommandServer(addr='127.0.0.1', port=8888)

@server.command
async def add(message, writer):
    reply = str(message['a'] + message['b'])
    writer.write(reply.encode())

server.run()
```

You can also run as a client, and connect to a sever:

```py
# pass address of server to connect to
client = jsonServer.Client(addr='127.0.0.1', port=8888)

# the client is a modified ExtendedServer so can accept commands just like the server
@client.command
async def pong(ctx):
    print("pong received!")

server.run()
```

Servers are event based, so you can hook into `on_connect(reader, writer)`, `on_message(ctx, message)`, `on_error(ctx, error)`
      and `on_disconnect(ctx, error)`, as well as making your own events:

```py
# define an event that is called every time a message is received. The leading "on_" is optional 
# (ie the function could just be called "message"). Note that this overwrites the default handler.
# you can't have multiple events, so you couldn't define a second "on_message" without overriding the first
@server.event
async def on_message(ctx, message):
    # call our custom event to log the message
    server.dispatch("our_custom_event", message)

    # since this overwrites the default handler, we have the oppertunity to manually handle the message
    # but let's just have the server handle it like normal
    server.handle_message(ctx, message)


# you can also make your own events; call them with "server.dispatch(event_name, *args, **kwargs)"
@server.event
async def on_our_custom_event(message):
    print("logging message", message)
```

By default, the server expects each message to consist of two bytes containing the length of the message, followed by the json message (because it uses TCP and it doesnt guarantee messages arrive all in one piece; you could only get the first half if you dont wait long enough) but you can change that to be whatever you want. For example, if you used websockets, which do guarantee messages arrive atomically, you could write:
```py
class Reader:
    def __init__(self, ws):
        self.ws = ws

    async def get_new_message(self):
        data = await self.ws.recv()
        try:
            return json.loads(data)
        except ValueError as e:
            raise JSONDecodeError(e, data)

class Writer:
    def __init__(self, ws):
        self.ws = ws

    async def send_message(self, message):
        await self.ws.send(message)

# note that for brevity the server here does not actually use websockets, see below for an example in a real project which does
# https://github.com/biglizards/RWCI_server/blob/master/ws_server.py

server = ExtendedServer(reader_obj=Reader, writer_obj=Writer)
```
For more examples of how I used this library, see [this project](https://github.com/biglizards/RWCI_server/blob/master/main.py)
