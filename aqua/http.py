"""
aqua.http -- Async HTTP feature
===============================

This module provides the HTTP Connection which designed for using with the :mod:`asyncio`
as describes :ref:`Transports and protocols (low-level API) <asyncio-protocol>`. Class
:class:`aqua.http.Connection` based on :class:`asyncio.Protocol` and can be used
with :meth:`asyncio.BaseEventLoop.create_server` to create HTTP server.

See the sample below which demonstrates using :class:`aqua.http.Connection`.

.. literalinclude:: ../demo/samplecon.py

Also it contains other classes and utility functions which help to builds async
HTTP applications.
"""
import io
import re
import sys
import webob
import asyncio
import logging
from webob import Response

logger = logging.getLogger('aqua.error')

_MAX_REQUEST_LINE = 2*1024  # Max size of HTTP request first line
_MAX_REQUEST_SIZE = 64*1024 # Max size of HTTP request except body


class Error(Exception):
    """ Simple HTTP Error
    
    Parameters the same as for :meth:`Connection.response` see it for more detail.
    """
    def __init__(self, status, headers=[], app_iter=[]):
        Exception.__init__(self, status, headers, app_iter)


class Request(webob.Request):
    """ HTTP request class (based on webob.Request)
    """
    @asyncio.coroutine
    def finish_reading(self, process_callback=None):
        """ Waits while body be read.
        
        :param process_callback: A callback that accepts two parameters:
            size of already loaded part of body and full body size.
        """
        total = self.content_length
        while not self.environ['aqua.complete']:
            if process_callback is not None:
                size = 0 if 'wsgi.input' not in self.environ else self.environ['wsgi.input'].tell()
                process_callback(size, total)
            yield from asyncio.sleep(0.001)
        if process_callback is not None:
            process_callback(total, total)
        return 


class Connection(asyncio.Protocol):
    """ HTTP Async Connection
    
    :param loop: :mod:`asyncio` event loop instance to use. If not set
                 default event loop instance will be used.
    """
    
    first_timeout = 0.2      #: Timeout for start reading first request from connection.
    request_timeout = 5.0    #: Timeout for reading a request headers and body.
    keepalive_timeout = 3.0  #: Timeout for waiting next request if connection is not been closed.
    #: Default request environ variables.
    default_environ = dict([
        ('wsgi.version', (1,0)), ('wsgi.url_scheme','http'),
        ('SERVER_PROTOCOL', 'HTTP/1.0'), ('SERVER_SOFTWARE', 'Aqua/DEV'),
        ('wsgi.multithread', False), ('wsgi.multiprocess', True), ('wsgi.run_once', False)])
    

    def __init__(self, loop=None):
        self._environ = None
        self._timeout = (0, None)
        self.loop = loop or asyncio.get_event_loop() #: :mod:`asyncio` event loop.


    def exception(self, message):
        """ Logs exception message. """
        logger.exception(message, extra=dict(ip=self.remote_addr[0]))
        
    def error(self, message):
        """ Logs error message. """
        logger.error(message, extra=dict(ip=self.remote_addr[0]))
        
    def warning(self, message):
        """ Logs warning message. """
        logger.warning(message, extra=dict(ip=self.remote_addr[0]))


    @property
    def local_addr(self):
        """ Local network address (ip, port). """
        return self.transport.get_extra_info('sockname')
    
    
    @property
    def remote_addr(self):
        """ Remote network address  (ip, port). """
        return self.transport.get_extra_info('peername')        
    

    @property
    def timeout(self):
        """ Returns or sets current I/O timeout. If it’s not set will return 0.
        If will be set 0 and timeout is present it will be unset. """
        return self._timeout[0]

    @timeout.setter
    def timeout(self, value):
        if self._timeout[1] is not None:
            self._timeout[1].cancel()
        self._timeout = (value, self.loop.call_later(value, self.connection_timeout)
                                if value > 0 else None)

    
    def connection_made(self, transport):
        """ Called when incomming HTTP connection is made.
        See more :meth:`asyncio.BaseProtocol.connection_made`."""
        self.transport = transport
        if 'SERVER_NAME' not in  self.default_environ:
            self.default_environ['SERVER_NAME'] = self.local_addr[0]
        if 'SERVER_PORT' not in  self.default_environ:
            self.default_environ['SERVER_PORT'] = str(self.local_addr[1])
        self.default_environ['REMOTE_ADDR'] = self.remote_addr[0]
        self.default_environ['wsgi.errors'] = sys.stderr
        self.default_environ['aqua.complete'] = False
        self.timeout = self.first_timeout


    def connection_lost(self, exc):
        """ Called when incomming HTTP connection is lost.
        See more :meth:`asyncio.BaseProtocol.connection_lost`."""
        if exc is not None:
            self.warning("Connection closed by: {0}".format(exc))


    def connection_timeout(self):
        """ Called when connection I/O timeout exceeded. """
        if self._environ is not None:
            self.response('408 Request Timeout', [], [])
        else:
            self.transport.close()
    
    def data_received(self, data):
        """ Called when some data is received.
        See more :meth:`asyncio.Protocol.data_received`."""
        if self._environ is None:
            self.start_request()
        try:
            if not self._header_received:
                self._buff = data
                if len(self._buff)>_MAX_REQUEST_SIZE:
                    raise Error('414 Request Too Long')
                pos = self._buff.find(b'\r\n\r\n')
                if pos>=0:
                    self._header_received = True
                    self._environ.update(parse_environ(self._buff[:pos+4]))
                    if 'CONTENT_TYPE' in self._environ:
                        self.body_chunk_received(self._environ, self._buff[pos+4:])
                        if self._environ.get('HTTP_EXPECT') == '100-continue':
                            self.expect_continue(self._environ)
                        else:
                            self.timeout = 0
                    else:
                        self._environ['aqua.complete'] = True
                    if asyncio.iscoroutinefunction(self.request_handler):
                        asyncio.Task(self.request_handler(self, self._environ))
                    else:
                        self.request_handler(self, self._environ)
            else:
                self.body_chunk_received(self._environ, data)
        except Error as exc:
            self.response(*exc.args)
        except Exception as exc:
            self.exception('Uncaught exception when reading request:')
            self.response('500 Internal Server Error', [], [])


    def start_request(self):
        """ Called when HTTP request is start reading. """
        self._buff = b''
        self._header_received = False
        self._environ = self.default_environ.copy()
        self.timeout = self.request_timeout
    

    def request_handler(self, connection, environ):
        """ Request handler. Must be overriden.
        
        :param environ: Request environ variables.
        :rtype: Tuple or list of three items. See parameters of :meth:`Connection.response` for more info.
        """
        connection.response('501 Not Implemented', [], [])


    def expect_continue(self, environ):
        """ Called when present header 'Expect: 100-continue'.
        
        :param environ: Request environ variables.
        """
        self.transport.write(b'HTTP/1.1 100 (Continue)\r\n\r\n')

    
    def body_chunk_received(self, environ, data):
        """ Called when chunk of body is received.
        
        :param environ: Request environ variables.
        :param data: Received chunk of body.
        :type data: bytes
        """
        assert not environ['aqua.complete']
        if 'wsgi.input' not in environ:
            environ['wsgi.input'] = io.BytesIO()
        if 'CONTENT_LENGTH' in environ:
            environ['wsgi.input'].write(data)
            if environ['wsgi.input'].tell() < int(environ['CONTENT_LENGTH']):
                return
        environ['aqua.complete'] = True
        environ['wsgi.input'].seek(0)
        self.timeout = 0
  

    def response(self, status, headers, app_iter):
        """ Outputs HTTP response.
        
        :param status: HTTP status string like '200 OK'
        :param headers: List of response headers represented as tuple (name, value)
        :param app_iter: Body iterator, item must be bytes.
        """
        self.timeout = 0
        code = int(status.split(' ')[0])
        if code<400:
            if 'HTTP_CONNECTION' in self._environ:
                close_connection = (self._environ['HTTP_CONNECTION']=='close')
            else:
                close_connection = (self._environ['SERVER_PROTOCOL']<'HTTP/1.1')
        else:
            close_connection = True
        self.transport.write("{0} {1}\r\n".format(self._environ['SERVER_PROTOCOL'], status).encode('ISO-8859-1'))
        for name, value in headers:
            if not close_connection and name=='Connection':
                close_connection = (value=='close')
            self.transport.write('{0}: {1}\r\n'.format(name, value).encode('ISO-8859-1'))
        self.transport.write(b'\r\n')
        for data in app_iter:
            self.transport.write(data)
        if close_connection:
            self.transport.close()
        else:
            self._environ = None
            self.timeout = self.keepalive_timeout


_quoted_slash = re.compile(b'(?i)%2F')        

def parse_environ(data):
    """ Parses request bytes data (except body) to request environ variables. """
    lines = data.split(b'\r\n')
    if len(lines[0])>_MAX_REQUEST_LINE:
        raise Error('414 Request Too Long')
    method, uri, version = lines[0].split(b' ')
    if version not in (b'HTTP/1.0',b'HTTP/1.1'):
        raise Error('505 HTTP Version Not Supported')
    parts = uri.split(b'?', 1)
    path, query = parts[0], parts[1] if len(parts)==2 else b''
    try:
        atoms = [unquote_bytes(x) for x in _quoted_slash.split(path)]
    except ValueError:
        raise Error('400 Bad Request')
    path = b'%2F'.join(atoms)
    result = dict(
        zip(('REQUEST_METHOD','REQUEST_URI','SERVER_PROTOCOL','SCRIPT_NAME', 'PATH_INFO', 'QUERY_STRING'),
             map(lambda item: item.decode('ISO-8859-1') ,(method, uri, version, b'', path, query))))
    name = None
    for item in map(lambda item: item.decode('ISO-8859-1'), lines[1:]):
        if item=='':
            break
        elif item[0] in (' ', '\t'):
            result[name] += item[0].strip()
        else:
            name, value = map(str.strip, item.split(':',1))
            name = name.upper().replace('-','_')
            if name not in ('CONTENT_TYPE','CONTENT_LENGTH'):
                name = 'HTTP_' + name
            if name in result:
                result[name] += ', ' + value
            else:
                result[name] = value
    return result


def unquote_bytes(data):
    """ Unqotes bytes string. """
    res = data.split(b'%')
    for i in range(1, len(res)):
        item = res[i]
        try:
            res[i] = bytes([int(item[:2], 16)]) + item[2:]
        except ValueError:
            raise
    return b''.join(res)