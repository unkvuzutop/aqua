import time
import tornado.web
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import asynchronous

class MainHandler(tornado.web.RequestHandler):
    
    @asynchronous
    @gen.coroutine
    def get(self):
        self.write("Hello, World!"*1024)
        

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(5002)
    IOLoop.instance().start()

"""
$ siege -c 100 -b -r 100 http://127.0.0.1:5002/

Transactions:		       10000 hits
Availability:		      100.00 %
Elapsed time:		        6.27 secs
Data transferred:	      126.95 MB
Response time:		        0.06 secs
Transaction rate:	     1594.90 trans/sec
Throughput:		       20.25 MB/sec
Concurrency:		       99.18
Successful transactions:       10000
Failed transactions:	           0
Longest transaction:	        0.09
Shortest transaction:	        0.01
"""

"""
$ siege -c 500 -b -r 100 http://127.0.0.1:5002/

Transactions:		       49949 hits
Availability:		       99.90 %
Elapsed time:		       56.28 secs
Data transferred:	      634.12 MB
Response time:		        0.41 secs
Transaction rate:	      887.51 trans/sec
Throughput:		       11.27 MB/sec
Concurrency:		      359.97
Successful transactions:       49949
Failed transactions:	          51
Longest transaction:	       26.75
Shortest transaction:	        0.01
"""