""" Sample chat application """
import time
import os.path
import asyncio
import logging
from webob.static import FileApp
from webob.exc import HTTPFound
from aqua.app import Application, handler
from jinja2 import Environment, PackageLoader

class AquaChat(Application):
    """Application class"""
    def __init__(self, loop, **kwargs):
        Application.__init__(self, loop, **kwargs)
        self.static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        self.jinja2_env = Environment(loader=PackageLoader('aquachat', 'templates'))
        self.jinja2_env.globals['url_for'] = self.url_for
        self.messages = list()
    
    
    @handler(r'/static/:filename')
    def static(self, request, filename):
        """ Static file serve handler."""
        return FileApp(os.path.join(self.static_path, filename))
    
    def redirect(self, url):
        return HTTPFound(location=url)
    
    def render_template(self, template, **kwargs):
        """Renders template"""
        template = self.jinja2_env.get_template(template)
        return template.render(**kwargs)
        
    
    @handler('/', ('GET', 'POST'))
    @handler('/user/:name', ('GET', 'POST'))
    def index(self, request, name=None):
        if request.method=='POST':
            yield from request.finish_reading()
            if name is not None:
                self.messages.append((time.time(), name, request.POST.get('message')))
                return 'OK'
            else:
                name = request.POST.get('name')
                if name is not None:
                    return self.redirect(self.url_for('index', name=name))
        return self.render_template('index.html', name=name)
    

    @handler('/chat', 'POST')
    def chat(self, request):
        left = 0
        last_messages = list()
        yield from request.finish_reading()
        name = request.POST.get('name')
        timestamp = float(request.POST.get('timestamp') or 0)
        while True:
            index = len(self.messages)-1
            if self.messages and self.messages[index][0] > timestamp:
                while index >= 0 and self.messages[index][0] > timestamp:
                    last_messages.insert(0, self.messages[index][1:])
                    index -= 1
                break
            else:
                if left >= 10.0:
                    break
                else:
                    yield from asyncio.sleep(0.5)
                    left += 0.5;
        timestamp = self.messages[len(self.messages)-1][0] if self.messages else timestamp
        return {'messages':last_messages, 'timestamp': timestamp}
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    
    app = AquaChat(asyncio.get_event_loop(), server_name='localhost')
    server = app.loop.run_until_complete(app.loop.create_server(app, '127.0.0.1', 5000))
    
    try:
        app.loop.run_forever()
    except KeyboardInterrupt:
        pass # Press Ctrl+C to stop
    finally:
        server.close() 