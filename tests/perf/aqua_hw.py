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
Elapsed time:		        5.90 secs
Data transferred:	      126.95 MB
Response time:		        0.06 secs
Transaction rate:	     1694.92 trans/sec
Throughput:		       21.52 MB/sec
Concurrency:		       98.91
Successful transactions:       10000
Failed transactions:	           0
Longest transaction:	        0.09
Shortest transaction:	        0.01
"""

"""
$ siege -c 500 -b -r 000 http://127.0.0.1:5000/

Transactions:		       34567 hits
Availability:		       96.78 %
Elapsed time:		       31.16 secs
Data transferred:	      438.84 MB
Response time:		        0.17 secs
Transaction rate:	     1109.34 trans/sec
Throughput:		       14.08 MB/sec
Concurrency:		      186.88
Successful transactions:       34567
Failed transactions:	        1151
Longest transaction:	       30.08
Shortest transaction:	        0.02

"""