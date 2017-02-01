import os
import spectralview.app
from tornado.options import define, options
import tornado.ioloop

define('db', default='mongodb://172.17.0.2:27017')
define('port', default='8000')

def main():
    """Entry point for the application script."""
    spectralview.app.Application().listen(int(options.port))
    print('listening on port {}'.format(options.port))
    tornado.ioloop.IOLoop.current().start()
