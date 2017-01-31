import os
import spectralview.app
from tornado.options import define, options, parse_command_line
import tornado.ioloop

define('db_ip', default=os.environ['DB_IP'])
define('db_port', default='27017')
define('port', default='8000')

def main():
    """Entry point for the application script."""
    parse_command_line()
    spectralview.app.Application().listen(int(options.port))
    print('listening on port {}'.format(options.port))
    tornado.ioloop.IOLoop.current().start()
