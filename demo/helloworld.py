import asyncio
import logging
from aqua.app import Application, handler

class SampleApplication(Application):
    
    @handler('/:user')
    def hello(self, request, user):
        yield from asyncio.sleep(2.0)
        return "Hello, {0}!".format("World" if user is None else user.capitalize()) 

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    app = SampleApplication(asyncio.get_event_loop(), server_name='localhost')
    server = app.loop.run_until_complete(app.loop.create_server(app, '127.0.0.1', 5000))
    
    try:
        app.loop.run_forever()
    except KeyboardInterrupt:
        pass # Press Ctrl+C to stop
    finally:
        server.close() 
