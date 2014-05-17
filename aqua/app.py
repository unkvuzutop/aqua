"""
aqua.app -- Async HTTP Application
==================================

This module provides the HTTP Application which designed for using with the :mod:`asyncio`
as describes :ref:`Transports and protocols (low-level API) <asyncio-protocol>`.
Application instance is callable. It's prepares and returns instance of :class:`aqua.http.Connection`
witch can be used with :meth:`asyncio.BaseEventLoop.create_server` to create HTTP server..

See the sample below which demonstrates simple HTTP Application.

.. literalinclude:: ../demo/helloworld.py
"""
import asyncio
import logging
from webob.exc import HTTPError
from aqua.router import TraversalRouter
from aqua.http import logger, Connection, Request, Response, logger


def handler(route, method='GET', **options):
    """ Decorator marks method to use as request handler.
    
    :param route: Route description.
    :param method: Request method or list of methods.
    :param options: Additional keyword options.
    """    
    def wrapper(view):
        if not hasattr(view, '_routes'):
            view._routes = list()
        if isinstance(method, (tuple, list)):
            for item in method:
                view._routes.append((route, item, options))
        else:
            view._routes.append((route, method, options))
        return view 
    return wrapper


class BaseApplication(object):
    """ Base application class
    
    :param loop: :mod:`asyncio` event loop instance to use.
    :param script_name: Default 'SCRIPT_NAME' used for routing
    """
    
    router_class = TraversalRouter #: Default router class
    
    def __init__(self, loop, script_name):
        self.loop = loop
        self._router = self.router_class()
        self.route = lambda *args, **kwargs : self._router.route(*args, **kwargs)
        self.url_for = lambda *args, **kwargs : self._router.url_for(*args, **kwargs)
        self.add_route = lambda *args, **kwargs : self._router.add_route(*args, **kwargs)
        
        self._script_name = script_name or '/'
        self._make_routes()

    def _make_routes(self):
        cls = self.__class__
        # finds routed methods   
        for name, value in cls.__dict__.items():
            if hasattr(value, '_routes'):
                for route, method, options in value._routes:
                    if not asyncio.iscoroutinefunction(value):
                        value = asyncio.coroutine(value)
                    self.add_route(route, method, value, **options)

    @asyncio.coroutine
    def request_router(self, environ):
        """ Routes and handles Request
        
        :param environ: Request environ variables.
        :rtype: Tuple or list of three items. See parameters of :meth:`aqua.http.Connection.response` for more info.
        """
        try:
            request = Request(environ)
            view, kwargs = self.route(request.path_info, request.method)
            result = yield from view(self, request, **kwargs)
        except HTTPError as exc:
            result = exc
        if not isinstance(result, Response):
            response = Response()
            if isinstance(result, str):
                response.text = result
            elif isinstance(result, bytes):
                if response.content_type=='text/html':
                    response.content_type = 'application/octet-stream'
                response.body = result
            elif isinstance(result, dict):
                response.content_type = 'application/json'
                response.json = result
            else:
                response = result
        else:
            response = result
        return request.call_application(response)  


class Application(BaseApplication):
    """ Application class
    
    :param loop: :mod:`asyncio` event loop instance to use.
        If not set default event loop instance will be used.
    :server_name: SERVER_NAME request environ variable if None value from connection
    :server_port: SERVER_PORT request environ variable if None value from connection
    """
    def __init__(self, loop=None, server_name=None, server_port=None):
        self.loop = loop or asyncio.get_event_loop()
        BaseApplication.__init__(self, loop, '/')
        self._app_environ = dict()
        if server_name is not None:
            self._app_environ['SERVER_NAME'] = server_name
        if server_name is not None:
            self._app_environ['SERVER_PORT'] = str(server_port)

    def __call__(self):
        connection = Connection(self.loop)
        connection.request_handler = self.request_router
        connection.default_environ.update(self._app_environ)
        return connection

    def sub_application(self, script_name, application_class):
        """ Binds sub application
        
        :param script_name: SCRIPT_NAME for sub application.
        :param application_class: Class of sub application.
        """
        assert issubclass(application_class, BaseApplication)
        app = application_class(self.loop, script_name)
        self._router.update(script_name, app._router)