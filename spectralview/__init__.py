import spectralview.app
import tornado.options
import tornado.ioloop

def main():
    """Entry point for the application script."""
    spectralview.app.Application().listen(8888)
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.current().start()
