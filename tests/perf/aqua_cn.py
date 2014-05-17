import asyncio
import logging
import aqua.http

class SampleConnection(aqua.http.Connection):
    
    def request_handler(self, connection, environ):
        connection.response('200 OK',
                [('Content-Type', 'text/html; charset=UTF-8'),
                 ('Content-Length', str(13*1024)),
                 ('Date','Sat, 17 May 2014 19:05:24 GMT'),
                 ('Server','AquaServer/0.1.5dev'),
                 ('ETag','"000000000000000000000000000000000000009e"'),
                ],[b"Hello, World!"*1024])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(loop.create_server(SampleConnection, '127.0.0.1', 5001))
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass # Press Ctrl+C to stop
    finally:
        server.close()

"""
$ siege -c 100 -b -r 100 http://127.0.0.1:5001/
Transactions:		       10000 hits
Availability:		      100.00 %
Elapsed time:		        3.13 secs
Data transferred:	      126.95 MB
Response time:		        0.03 secs
Transaction rate:	     3194.89 trans/sec
Throughput:		       40.56 MB/sec
Concurrency:		       98.70
Successful transactions:       10000
Failed transactions:	           0
Longest transaction:	        0.06
Shortest transaction:	        0.02
"""

"""
$ siege -c 500 -b -r 1000 http://127.0.0.1:5001/

Transactions:		       49845 hits
Availability:		       99.69 %
Elapsed time:		       33.88 secs
Data transferred:	      632.80 MB
Response time:		        0.15 secs
Transaction rate:	     1471.22 trans/sec
Throughput:		       18.68 MB/sec
Concurrency:		      214.28
Successful transactions:       49845
Failed transactions:	         155
Longest transaction:	       22.78
Shortest transaction:	        0.01
"""


"""
$ siege -c 1000 -b -r 1000 http://127.0.0.1:5001/

Transactions:		       99165 hits
Availability:		       99.17 %
Elapsed time:		       54.65 secs
Data transferred:	     1258.93 MB
Response time:		        0.41 secs
Transaction rate:	     1814.55 trans/sec
Throughput:		       23.04 MB/sec
Concurrency:		      743.62
Successful transactions:       99165
Failed transactions:	         835
Longest transaction:	        7.03
Shortest transaction:	        0.00

"""


