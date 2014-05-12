import asyncio
import logging
import aqua.http

class SampleConnection(aqua.http.Connection):
    
    @asyncio.coroutine
    def request_handler(self, environ):
        def app_iter():
            yield b'<h3>Environ</h3><table>'
            for name, value in sorted(environ.items()):
                yield b'<tr>'
                yield "<td>{}</td>".format(name).encode('ISO-8859-1')
                yield "<td>{}</td>".format(value).encode('ISO-8859-1')
                yield b'</tr>'
            yield b'</table>'
        return '200 OK', [('Content-Type', 'text/html'), ('Connection', 'close')], app_iter()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(loop.create_server(SampleConnection, '127.0.0.1', 5000))
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass # Press Ctrl+C to stop
    finally:
        server.close()