import asyncio
import logging
from datetime import datetime
from aqua.http import Response
from aqua.app import Application, handler

class SampleApplication(Application):
    
    @handler('/:user')
    def hello(self, request, user):
        response = Response("Hello, World!"*1024)
        response.date = datetime.now()
        response.server = 'AquaServer/0.1.5dev'
        response.etag = '000000000000000000000000000000000000009e'
        return response

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    app = SampleApplication(asyncio.get_event_loop(), server_name='localhost')
    server = app.loop.run_until_complete(app.loop.create_server(app, '127.0.0.1', 5000))
    
    try:
        app.loop.run_forever()
    except KeyboardInterrupt:
        pass # Press Ctrl+C to stop
    finally:
        server.close()
"""
$ siege -c 100 -b -r 100 http://127.0.0.1:5000/

Transactions:		       10000 hits
Availability:		      100.00 %
Elapsed time:		        5.58 secs
Data transferred:	      126.95 MB
Response time:		        0.06 secs
Transaction rate:	     1792.11 trans/sec
Throughput:		       22.75 MB/sec
Concurrency:		       99.08
Successful transactions:       10000
Failed transactions:	           0
Longest transaction:	        0.07
Shortest transaction:	        0.01
"""

"""
$ siege -c 500 -b -r 000 http://127.0.0.1:5000/

Transactions:		       49709 hits
Availability:		       99.42 %
Elapsed time:		       34.42 secs
Data transferred:	      631.07 MB
Response time:		        0.14 secs
Transaction rate:	     1444.19 trans/sec
Throughput:		       18.33 MB/sec
Concurrency:		      197.66
Successful transactions:       49709
Failed transactions:	         291
Longest transaction:	       30.76
Shortest transaction:	        0.00
"""

"""
$ siege -c 1000 -b -r 000 http://127.0.0.1:5000/

Transactions:		       61921 hits
Availability:		       97.99 %
Elapsed time:		       80.38 secs
Data transferred:	      786.11 MB
Response time:		        0.76 secs
Transaction rate:	      770.35 trans/sec
Throughput:		        9.78 MB/sec
Concurrency:		      588.02
Successful transactions:       61921
Failed transactions:	        1267
Longest transaction:	       40.76
Shortest transaction:	        0.00
"""