"""
aqua.router -- Router
=====================
"""

from itertools import zip_longest
from webob.exc import HTTPMethodNotAllowed, HTTPNotFound


class _RouteItem(object):
    """ Class of object describe item of route based on traversal. """
    
    def __init__(self):
        self.routes = dict()
        self.methods = dict()
    
    def __call__(self, split_path, method):
        """ Route resolver"""
        item = self.methods.get(method, (None,))
        view, argnames = item[0], item[1:]
        if view is not None and len(argnames)>=len(split_path):
            return view, dict(zip_longest(argnames, split_path)) # view found
        elif self.routes is not None and len(split_path)>0 and split_path[0] in self.routes:
            return self.routes[split_path[0]](split_path[1:], method) # has subroute item
        else:
            if len(split_path)==0:
                return None, tuple(self.methods.keys())  # 405
            else:
                return None, () # 404

    
    def add(self, split_path, method, view, *argnames):
        """ Adds route item"""
        if len(split_path)==0:
            if method in self.methods:
                raise ValueError("Route with some method already exists.")
            if len(argnames)>0:
                if self.routes is not None and len(self.routes)>0:
                    raise ValueError("Route with some part of path already exists.")
                self.routes = None
            self.methods[method] = (view,)+argnames
        else:
            if self.routes is not None:
                if split_path[0] not in self.routes:
                    self.routes[split_path[0]] = _RouteItem()
                self.routes[split_path[0]].add(split_path[1:], method, view, *argnames)
            else:
                raise ValueError("Route with some part of path already exists.")


class TraversalRouter(object):
    """ Router based on traversal method. """
    
    def __init__(self):
        self._views = dict()
        self._routes = _RouteItem()
        
    def route(self, path_info, method):
        """Resolves route for request described given arguments
        
        :param path_info: Request path.
        :param method: Request method.
        :rtype: Tuple of two items: correspond method an its urlvars as dict.
        """
        split_path = path_info.split('/')[1:]
        split_path = [] if split_path==[''] else split_path
        view, kwargs = self._routes(split_path, method)
        if view is None:
            if len(kwargs)>0:
                raise HTTPMethodNotAllowed(headers=[('Allow', ','.join(kwargs))])
            else:
                raise HTTPNotFound()
        return view, kwargs
    
    def add_route(self, route, method, view, **options):
        """ Adds route
        
        :param route: Route description.
        :param method: Request method or list of methods.
        :param view: Application method which correspond to this route.
        :param options: Additional keyword options.
        """
        argnames = list()
        split_path = list()
        parts = route.split('/')[1:]
        parts = [] if parts==[''] else parts
        for part in parts:
            if part[0]!=':':
                if len(argnames)==0:
                    split_path.append(part)
                else:
                    raise ValueError("Parameter 'path' has wrong value '{0}'.".format(path))
            else:
                argnames.append(part[1:])
        try:
            self._routes.add(split_path, method, view, *argnames)
        except ValueError:
            raise ValueError("Route bad or corresponding for '{0} {1}' already exists.".format(method, route))
        # adds view name
        view_name = options.get('name', view.__name__)
        if view_name not in self._views:
            self._views[view_name] = list()
        item = ('/'+'/'.join(split_path),)+tuple(argnames)
        if item not in self._views[view_name]:
            self._views[view_name].append(item)
            self._views[view_name] = list(reversed(sorted(self._views[view_name])))

            
    def url_for(self, view_name, **kwargs):
        result = None
        found_none = False
        for item in self._views.get(view_name, list()):
            path, argnames = item[0], item[1:]
            if len(argnames)>=len(kwargs.keys()) and set(kwargs.keys()).issubset(set(argnames)):
                result = path.split('/')
                for name in argnames:
                    part = kwargs.get(name)
                    found_none = True if part is None else found_none
                    if part is not None:
                        if not found_none:
                            result.append(part)
                        else:
                            result = None
                            break
        if result is not None:
            result = '/'.join(result)
        return result            
