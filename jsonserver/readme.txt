inspired by d.py

three layers of features (with BaseServer as the least and ExtendedServer as the most complex and featured):
  BaseServer:
    - defines the event decorator and dispatching system
      - events can be anything, although the only one dispatched by this server is on_connect
    - includes a default run command
    - everything else must be written by the user
    Example:
      ```
      import jsonServer
      server = jsonServer.BaseServer()
      @server.event
      async def on_connect(reader, writer):
          writer.write(b'hello')
      sever.run(host='0.0.0.0', port=8888)
      ```
  Command server:
    - all of the above
    - dispatches on_connect(reader, writer), on_message(message, writer), on_error(error) and on_disconnect(error)
    - defines the command decorator
    - commands can be sent to the server in the format `{"command": "foo", "bar": 5}` where bar is an argument
      - note that the name of the command field can be changed via `server.command_field_name`
    - commands are passed the message and a stream writer, in that order
    - includes default on_connect and on_message functions that utilise the command system
    - creates a (replaceable) wrapper for the stream reader implementing the following spec:
      > all messages to the server should be valid json
      > the two bytes sent before the message must be a big endian small containing the length of the message
      > as such no messages may be above 65535 bytes (64KB)
    - feel free to swap it out with one implementing your own
    Example:
      ```
      import jsonServer
      server = jsonServer.CommandServer()
      @server.command
      async def add(message, writer):
          reply = str(message['a'] + message['b'])
          writer.write(reply.encode())
      server.run()
      ```
  Extended server:
    - all of the above
    - by default, dispatches on_connect(reader, writer), on_message(ctx, message), on_error(ctx, e)
      and on_disconnect(ctx, e)
    - creates a (replaceable) wrapper for the stream writer implementing the above spec, as well as allowing dicts
      and strings to be sent via writer.send_message()
    - creates a context object (which probably should have just been a named tuple) containing the message sent,
      the server object, the writer, and the command invoked
    - made changes to the way commands work:
      - commands are passed a context object and then the arguments in the style (ctx, **message) although without
        the command as part of the message
        - ie the message `{"command": "foo", "bar": 5}` would be accepted by the function `def foo(ctx, bar)`
      - commands are no longer directly passed the writer, although it is available via the context object, but are
        instead encouraged to give their reply via their return value
        - an optional default value may be set for functions that return None (eg a generic success message)
    Example:
      ```
      import jsonServer
      server = jsonServer.ExtendedServer()
      @server.command
      async def add(ctx, a, b):
          return a + b
      server.run()
      ```
  there's also cogs which you can use with any of them
