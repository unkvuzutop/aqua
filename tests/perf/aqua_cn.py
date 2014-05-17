import asyncio
import logging
import aqua.http

class SampleConnection(aqua.http.Connection):
    
    @asyncio.coroutine
    def request_handler(self, environ):
        return ('200 OK',
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
Elapsed time:		        4.33 secs
Data transferred:	      126.95 MB
Response time:		        0.04 secs
Transaction rate:	     2309.47 trans/sec
Throughput:		       29.32 MB/sec
Concurrency:		       97.68
Successful transactions:       10000
Failed transactions:	           0
Longest transaction:	        0.22
Shortest transaction:	        0.00
"""

"""
$ siege -c 500 -b -r 000 http://127.0.0.1:5001/

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
$ siege -c 1000 -b -r 000 http://127.0.0.1:5001/

Transactions:		       68971 hits
Availability:		       98.37 %
Elapsed time:		       78.42 secs
Data transferred:	      875.61 MB
Response time:		        0.50 secs
Transaction rate:	      879.51 trans/sec
Throughput:		       11.17 MB/sec
Concurrency:		      438.53
Successful transactions:       68971
Failed transactions:	        1144
Longest transaction:	       40.04
Shortest transaction:	        0.00
"""
