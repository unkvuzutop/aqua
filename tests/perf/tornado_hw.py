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

Transactions:		       49952 hits
Availability:		       99.90 %
Elapsed time:		       48.48 secs
Data transferred:	      634.16 MB
Response time:		        0.40 secs
Transaction rate:	     1030.36 trans/sec
Throughput:		       13.08 MB/sec
Concurrency:		      408.49
Successful transactions:       49952
Failed transactions:	          48
Longest transaction:	       16.22
Shortest transaction:	        0.01
"""

"""
$ siege -c 1000 -b -r 100 http://127.0.0.1:5002/

Transactions:		       99498 hits
Availability:		       99.50 %
Elapsed time:		       88.90 secs
Data transferred:	     1263.16 MB
Response time:		        0.57 secs
Transaction rate:	     1119.21 trans/sec
Throughput:		       14.21 MB/sec
Concurrency:		      640.26
Successful transactions:       99498
Failed transactions:	         502
Longest transaction:	       17.55
Shortest transaction:	        0.01
"""