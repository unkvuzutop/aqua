# -*- coding: utf-8 -*-
import asyncio
import aqua.http
from collections import deque


class TestTransport(object):
    def __init__(self, connection):
        self._buff = b''
        self._conn = connection
    
    def write(self, data):
        self._buff += data
    
    def close(self):
        self._conn.connection_lost(None)
    

class TestConnection(aqua.http.Connection):
    
    def connection_made(self, transport):
        aqua.http.Connection.connection_made(self, transport)
        transport.write(b'#CONNECTION_MADE#\r\n')

    def start_request(self):
        aqua.http.Connection.start_request(self)
        self.transport.write(b'#START_REQUEST#\r\n')
    
    def connection_lost(self, exc):
        aqua.http.Connection.connection_lost(self, exc)
        self.transport.write(b'#CONNECTION_CLOSED#\r\n')
        self.loop.stop()


def test_RequestProcess():

    stack = deque()
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def request_handler_head(connection, environ):
        assert environ.get('REQUEST_METHOD')=='HEAD'
        assert environ.get('SERVER_PROTOCOL')=='HTTP/1.0'
        assert environ.get('PATH_INFO').encode('ISO-8859-1').decode('UTF-8')=='/wiki/HTTP Запрос'
        assert environ.get('QUERY_STRING')=='last=Y&K'
        assert environ.get('REMOTE_ADDR')=='athost'
        assert environ.get('SERVER_NAME')=='myhost'
        assert environ.get('SERVER_PORT')=='8080'
        assert environ.get('HTTP_HOST')=='ru.wikipedia.org'
        assert environ.get('HTTP_SET_COOKIE')=='c1=100; path=/; domain=localhost, c5=500; path=/; domain=localhost'
        assert environ.get('aqua.complete')==True
        connection.response('200 OK', [('Content-Length','text/plain'), ('Content-Length','13')], [b'Hello, World!'])
    
    @asyncio.coroutine
    def request_handler_post(connection, environ):
        assert environ.get('REQUEST_METHOD')=='POST'
        assert environ.get('SERVER_PROTOCOL')=='HTTP/1.1'
        assert environ.get('PATH_INFO')=='/wiki/article'
        assert environ.get('QUERY_STRING')==''
        assert environ.get('aqua.complete')==False
        request = aqua.http.Request(environ)
        assert request.content_type == 'text/plain'
        assert request.content_length == 50
        yield from request.finish_reading(
            lambda size, length: trans.write('#BODY_CHUNK#{0}#{1}#\r\n'.format(size, length).encode('UTF-8'))
        )
        assert environ.get('aqua.complete')==True
        assert request.body == b'0123456789\r\n'*4+b'\r\n'
        connection.response('200 OK', [], [])

    
    def factory():
        conn = TestConnection(loop)
        stack.appendleft(conn)
        return conn
    
    server = loop.run_until_complete(loop.create_server(factory(), '127.0.0.1', 5000))
    conn = stack.popleft()
    trans = TestTransport(conn)
    trans.get_extra_info = lambda name: ('myhost', 8080) if name=='sockname' else ('athost', 9090)
    conn.connection_made(trans)
    
    @asyncio.coroutine
    def test_01():
        conn.request_handler = request_handler_head
        conn.data_received(b'HEAD /wiki/HTTP%20%D0%97%D0%B0%D0%BF%D1%80%D0%BE%D1%81?last=Y&K HTTP/1.0\r\n'
                           b'Host: ru.wikipedia.org\r\n'
                           b'Connection: keep-alive\r\n'
                           b'Set-Cookie: c1=100; path=/; domain=localhost\r\n'
                           b'Set-Cookie: c5=500; path=/; domain=localhost\r\n'
                           b'\r\n')
        yield from asyncio.sleep(0.1)
        conn.request_handler = request_handler_post
        conn.data_received(b'POST /wiki/article HTTP/1.1\r\n'
                           b'Host: ru.wikipedia.org\r\n'
                           b'Content-Type: text/plain\r\n'
                           b'Content-Length: 50\r\n'
                           b'Connection: close\r\n'
                           b'\r\n'
                           b'0123456789\r\n')
        yield from asyncio.sleep(0.002)
        conn.data_received(b'0123456789\r\n'
                           b'0123456789\r\n'
                           b'0123456789\r\n'
                           b'\r\n')
    
    
    asyncio.async(test_01())
    loop.run_forever()
    loop.close()
    assert trans._buff==(b'#CONNECTION_MADE#\r\n'
                         b'#START_REQUEST#\r\n'
                         b'HTTP/1.0 200 OK\r\n'
                         b'Content-Length: text/plain\r\n'
                         b'Content-Length: 13\r\n'
                         b'\r\n'
                         b'Hello, World!'
                         b'#START_REQUEST#\r\n'
                         b'#BODY_CHUNK#12#50#\r\n'
                         b'#BODY_CHUNK#12#50#\r\n'
                         b'#BODY_CHUNK#50#50#\r\n'
                         b'HTTP/1.1 200 OK\r\n'
                         b'\r\n'
                         b'#CONNECTION_CLOSED#\r\n')

if __name__ == '__main__':
    
    test_RequestProcess()