import os
import uuid
import io
import json
import tornado.web
import tornado.websocket
from tornado.options import define, options
import motor.motor_tornado
from matplotlib.backends.backend_webagg_core import \
        FigureManagerWebAgg, \
        new_figure_manager_given_figure
from matplotlib.figure import Figure
from matplotlib._pylab_helpers import Gcf
from spectralview.fits import parse_fits
from bson.objectid import ObjectId


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie('user')


class FigureHandler(BaseHandler):
    """Create figure and render its page."""
    async def get(self, spectrum_id):
        spectrum = await self.db.spectra.find_one({'_id': ObjectId(spectrum_id)})
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(spectrum['wave'], spectrum['flux'])
        ax.set_title(spectrum['name'])
        fig_num = id(fig)
        manager = new_figure_manager_given_figure(fig_num, fig)
        Gcf.set_active(manager)
        self.render('figure.html', host=self.request.host, fig_num=fig_num)


class MplJsHandler(BaseHandler):
    def get(self):
        self.set_header('Content-Type', 'application/javascript')
        js = FigureManagerWebAgg.get_javascript()
        self.write(js)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, fig_num):
        self.supports_binary = True
        self.manager = Gcf.get_fig_manager(int(fig_num))
        self.manager.add_web_socket(self)
        if hasattr(self, 'set_nodelay'):
            self.set_nodelay(True)

    def on_close(self):
        self.manager.remove_web_socket(self)

    def on_message(self, message):
        message = json.loads(message)
        if message['type'] == 'supports_binary':
            self.supports_binary = message['value']
        else:
            self.manager.handle_json(message)

    def send_json(self, content):
        self.write_message(json.dumps(content))

    def send_binary(self, blob):
        if self.supports_binary:
            self.write_message(blob, binary=True)
        else:
            data = 'data:image/png;base64,{}'.format(
                    blob.encode('base64').replace('\n', '')
                    )
            self.write_message(data)


class SpectraHandler(BaseHandler):
    async def get(self):
        """Display all spectra"""
        spectra = []
        async for spectrum in self.db.spectra.find():
            spectra.append(spectrum)
        self.render('show_spectra.html', spectra=spectra)

    @tornado.web.authenticated
    async def post(self):
        data = parse_fits(io.BytesIO(self.request.files['file'][0]['body']))
        await self.db.spectra.insert_one(data)
        self.redirect(self.reverse_url('index'))


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', error=None)

    async def post(self):
        username = self.get_argument('username')
        user = await self.db.users.find_one({'username': username})
        if not user:
            self.render('login.html', error='user not found')
            return
        if self.get_argument('password') == user['password']:
            self.set_secure_cookie('user', username)
            self.redirect(self.reverse_url('index'))
        else:
            self.render('login.html', error='incorrect password')


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect(self.reverse_url('index'))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                tornado.web.URLSpec(r'/', SpectraHandler, name='index'),
                tornado.web.URLSpec(r'/spectra/([0-9a-z]+)', FigureHandler, name='spectrum'),
                tornado.web.URLSpec(r'/mpl.js', MplJsHandler, name='mpl'),
                tornado.web.URLSpec(r'/([0-9]+)/ws', WebSocketHandler, name='ws'),
                tornado.web.URLSpec(r'/login', LoginHandler, name='login'),
                tornado.web.URLSpec(r'/logout', LogoutHandler, name='logout'),
                ]
        setting = dict(
                template_path=os.path.join(os.path.dirname(__file__), 'templates'),
                static_path=os.path.join(os.path.dirname(__file__), 'static'),
                debug=True,
                login_url='/login',
                cookie_secret=str(uuid.uuid4()),
                xsrf_cookies=True,
                )
        super(Application, self).__init__(handlers, **setting)

        self.db = motor.MotorClient(options.db_ip, int(options.db_port)).spectalview
        self.db.users.insert_one({'username': 'admin', 'password': 'default'})
