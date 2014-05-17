# -*- coding: utf-8 -*-
import asyncio
from aqua.app import BaseApplication, Application, handler

class SubApplication(BaseApplication):
    @handler('/:name')
    def index(self, request, name):
        return "Hello, {0}!".format("World" if name is None else name.capitalize()) 

class TestApplication(Application):
    
    @handler('/')
    def index(self, request):
        return 'Index'
    
    @handler('/user/:name')
    def hello(self, request, name):
        return {"name": None if name is None else name.capitalize()}
    
    @handler('/binary')
    def binary(self, request):
        return b'\t\t\t\t\t'

loop = asyncio.get_event_loop()
app = TestApplication(asyncio.get_event_loop(), server_name='localhost')
app.sub_application('/sub/hello', SubApplication)
    
def test_Router():
    
    @asyncio.coroutine
    def test_01():
        environ = dict(app._app_environ.items())
        environ['REQUEST_METHOD'] = 'GET'
        environ['PATH_INFO'] = '/'
        result = yield from app.request_router(environ)
        assert result==('200 OK', [('Content-Type', 'text/html; charset=UTF-8'), ('Content-Length', '5')], [b'Index'])

    @asyncio.coroutine
    def test_02():
        environ = dict(app._app_environ.items())
        environ['REQUEST_METHOD'] = 'GET'
        environ['PATH_INFO'] = '/user/ivan'
        result = yield from app.request_router(environ)
        assert result==('200 OK', [('Content-Type', 'application/json; charset=UTF-8'), ('Content-Length', '15')], [b'{"name":"Ivan"}'])

    @asyncio.coroutine
    def test_02a():
        environ = dict(app._app_environ.items())
        environ['REQUEST_METHOD'] = 'GET'
        environ['PATH_INFO'] = '/user'
        result = yield from app.request_router(environ)
        assert result==('200 OK', [('Content-Type', 'application/json; charset=UTF-8'), ('Content-Length', '13')], [b'{"name":null}'])

    @asyncio.coroutine
    def test_03():
        environ = dict(app._app_environ.items())
        environ['REQUEST_METHOD'] = 'GET'
        environ['PATH_INFO'] = '/binary'
        result = yield from app.request_router(environ)
        assert result==('200 OK', [('Content-Type', 'application/octet-stream; charset=UTF-8'), ('Content-Length', '5')], [b'\t\t\t\t\t'])

    @asyncio.coroutine
    def test_04():
        environ = dict(app._app_environ.items())
        environ['REQUEST_METHOD'] = 'GET'
        environ['PATH_INFO'] = '/foo'
        result = yield from app.request_router(environ)
        assert result[0]=='404 Not Found'
        
    @asyncio.coroutine
    def test_05():
        environ = dict(app._app_environ.items())
        environ['REQUEST_METHOD'] = 'POST'
        environ['PATH_INFO'] = '/'
        result = yield from app.request_router(environ)
        assert result[0]=='405 Method Not Allowed'
        assert ('Allow', 'GET') in result[1]

    @asyncio.coroutine
    def test_06():
        environ = dict(app._app_environ.items())
        environ['REQUEST_METHOD'] = 'GET'
        environ['PATH_INFO'] = '/sub/hello/ivan'
        result = yield from app.request_router(environ)
        print(result)
        assert result==('200 OK', [('Content-Type', 'text/html; charset=UTF-8'), ('Content-Length', '12')], [b'Hello, Ivan!'])

    
    loop.run_until_complete(asyncio.async(test_01()))
    loop.run_until_complete(asyncio.async(test_02()))
    loop.run_until_complete(asyncio.async(test_02a()))
    loop.run_until_complete(asyncio.async(test_03()))
    loop.run_until_complete(asyncio.async(test_04()))
    loop.run_until_complete(asyncio.async(test_05()))
    loop.run_until_complete(asyncio.async(test_06()))


def test_url_for():
    assert app.url_for('index')=='/'
    assert app.url_for('hello')=='/user'
    assert app.url_for('hello', name='ivan')=='/user/ivan'
    assert app.url_for('foo', name='ivan') is None
    assert app.url_for('index', name='ivan') is None
    
    assert app.url_for('sub:hello:index')=='/sub/hello'
    assert app.url_for('sub:hello:index', name='ivan')=='/sub/hello/ivan'
    assert app.url_for('sub:hello:hello', name='ivan') is None
    assert app.url_for('sub:foo:index', name='ivan') is None

if __name__ == '__main__':
    
    test_Router()
    test_url_for()
