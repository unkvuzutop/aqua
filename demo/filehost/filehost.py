import os.path
import asyncio
from os import listdir
from jinja2 import Template
from webob.static import FileApp
from aqua.app import Application, handler

template = Template("""<!DOCTYPE html>
<html>
<head><title>My Files</title></head>
</body>
<h3>List of files:</h3>
<ul>
  {% for item, url in files %}
    <li><a href="{{url}}">{{item}}</a></li>
  {% endfor %}
</ul>
</body>
</html>
""")

class Filehost(Application):
    """Demo application class"""
    def __init__(self, loop, **kwargs):
        Application.__init__(self, loop, **kwargs)
        self.static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    @handler(r'/static/:filename')
    def static(self, request, filename):
        return FileApp(os.path.join(self.static_path, filename))    
    
    @handler('/')
    def index(self, request):
        def dir(path, files=[], prefix=None):
            for filename in listdir(path):
                if os.path.isfile(os.path.join(path, filename)):
                    filename = prefix+'/'+filename if prefix else filename
                    files.append((filename, self.url_for('static', filename=filename)))
            return files
        return template.render(files=dir(os.path.join(os.path.dirname(__file__), 'static')))

if __name__ == '__main__':

    import os.path
    app = Filehost(asyncio.get_event_loop())
    server = app.loop.run_until_complete(app.loop.create_server(app, '127.0.0.1', 5000))
    try:
        app.loop.run_forever()
    except KeyboardInterrupt:
        pass # Press Ctrl+C to stop
    finally:
        server.close()
