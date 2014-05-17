from nose.tools import assert_raises
from aqua.app import TraversalRouter, handler
from webob.exc import HTTPMethodNotAllowed, HTTPNotFound

router = TraversalRouter()

class Test(object):
    
    def route_0(self):
        return 'route#0'
    
    @handler('/user/:name', ('GET', 'POST'), name='user')
    def route_1(self):
        return 'route#1'


def test_RouteAdd():
    router.add_route('/', 'GET', Test.route_0, name='index')
    assert Test.route_1._routes==[('/user/:name', 'GET', {'name': 'user'}), ('/user/:name', 'POST', {'name': 'user'})]
    route, method, options = Test.route_1._routes[0]
    router.add_route(route, method, Test.route_1, **options)
    route, method, options = Test.route_1._routes[1]
    router.add_route(route, method, Test.route_1, **options)
    router.add_route('/article', 'GET', Test.route_0, name='article')
    router.add_route('/article/latest', 'GET', Test.route_0, name='latest')
    router.add_route('/article/new/:id', 'POST', Test.route_0, name='new')
    
    sub_router = TraversalRouter()
    sub_router.add_route('/', 'GET', Test.route_0, name='index')
    sub_router.add_route('/user/:name', 'GET', Test.route_1, name='user')
    sub_router.add_route('/user/:name', 'POST', Test.route_1, name='user')
    router.update('/sub', sub_router)
    assert_raises(ValueError, router.update, '/', sub_router)
    assert_raises(ValueError, router.update, '/user/sub', sub_router)
    
    router.add_route('/sub/article/new/:id/:kk', 'POST', Test.route_0, name='new')
    assert_raises(ValueError, router.add_route, '/sub/user/:name', 'POST', Test.route_1, name='user')
    
    
def test_RouteResolve():
    assert router.route('/', 'GET')==(Test.route_0, {})
    assert_raises(HTTPMethodNotAllowed, router.route, '/', 'POST')
    assert router.route('/user', 'GET')==(Test.route_1, {'name':None})
    assert router.route('/user/ivan', 'GET')==(Test.route_1, {'name':'ivan'})
    assert_raises(HTTPNotFound, router.route, '/user/ivan/0/0', 'GET')
    assert_raises(HTTPNotFound, router.route, '/ivan/0/0', 'GET')
    assert_raises(HTTPNotFound, router.route, '/ivan/0/0', 'POST')
    assert router.route('/article', 'GET')==(Test.route_0, {})
    assert_raises(HTTPNotFound, router.route, '/article/0', 'GET')
    assert_raises(HTTPNotFound, router.route, '/article/0', 'POST')
    assert router.route('/article/latest', 'GET')==(Test.route_0, {})
    assert_raises(HTTPMethodNotAllowed, router.route, '/article/new', 'GET')
    assert router.route('/article/new', 'POST')==(Test.route_0, {'id':None})
    assert router.route('/article/new/007', 'POST')==(Test.route_0, {'id':'007'})
    
    assert router.route('/sub', 'GET')==(Test.route_0, {})
    assert_raises(HTTPMethodNotAllowed, router.route, '/sub', 'POST')
    assert router.route('/sub/user', 'GET')==(Test.route_1, {'name':None})
    assert router.route('/sub/user/ivan', 'GET')==(Test.route_1, {'name':'ivan'})
    assert router.route('/sub/user/ivan', 'POST')==(Test.route_1, {'name':'ivan'})
    
    assert_raises(HTTPNotFound, router.route, '/sub/article', 'POST')
    assert router.route('/sub/article/new/777', 'POST')==(Test.route_0, {'id':'777', 'kk':None})
    
    assert router._views == {
        'user': [('/user', 'name')],
        'latest': [('/article/latest', )],
        'index': [('/', )],
        'new': [('/sub/article/new', 'id', 'kk'), ('/article/new', 'id')],
        'article': [('/article', )],
        'sub:index': [('/sub', )],
        'sub:user': [('/sub/user', 'name')],
    }

if __name__ == '__main__':
    test_RouteAdd()
    test_RouteResolve()