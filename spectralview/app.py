import os
import io
import uuid
import json
import tornado.web
from tornado.web import URLSpec
import tornado.websocket
from tornado.options import define, options, parse_command_line
import motor.motor_tornado
from matplotlib.backends.backend_webagg_core import \
        FigureManagerWebAgg, \
        new_figure_manager_given_figure
from spectralview.fits import parse_fits, download_fits
import spectralview.utils as utils
import spectralview.ssap as ssap
from bson.objectid import ObjectId


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie('user')


class ExportHandler(BaseHandler):
    async def get(self):
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename=spectra.csv')
        async for spectrum in self.db.spectra.find({'label': {'$gt':-1}}):
            self.write(spectrum['ident'] + ',' + str(spectrum['label']) + '\n')
        self.finish()


class ClassifyHandler(BaseHandler):
    async def get(self):
        # TODO make function which download if not exist
        spectrum = await self.db.spectra.find_one({'label': -1})
        try:
            wave, flux = spectrum['wave'], spectrum['flux']
        except KeyError:
            fits_dict = download_fits(spectrum['ident'])
            ident = {'_id': ObjectId(spectrum['_id'])}
            if fits_dict == None:
                result = await self.db.spectra.delete_many(ident)
                self.redirect(self.reverse_url('classify'))
                return
            await self.db.spectra.update_one(ident, {'$set': fits_dict})
            spectrum = await self.db.spectra.find_one(ident)
            wave, flux = spectrum['wave'], spectrum['flux']
        self.render('classify.html', spectrum=spectrum)

    async def post(self):
        label = self.get_argument('label')
        label_dict = {'label': 2}   # default is unknown
        if label == 'emission':
            label_dict['label'] = 0
        elif label == 'absorption':
            label_dict['label'] = 1

        ident_dict = {'_id': ObjectId(self.get_argument('ident'))}
        await self.db.spectra.update_one(ident_dict, {'$set': label_dict})
        self.redirect(self.reverse_url('classify'))


class ClassificationHandler(BaseHandler):
    async def get(self):
        spectra = []
        async for spectrum in self.db.spectra.find({'label': -1}):
            spectra.append(spectrum)
        self.render('classification.html', spectra=spectra)

    async def post(self):
        # parse POST request
        service_url = self.get_argument('service_url')
        band = self.get_argument('band')
        # creta URL for query
        ssap_url = ssap.make_ssap_url(url=service_url, band=band)
        # fetch the URL
        response = utils.request_url(ssap_url)
        # parse ids
        ids = set(ssap.get_ids(response.body))
        # update db
        old_ids = set()
        async for spectrum in self.db.spectra.find():
            old_ids.add(spectrum['ident'])
        ids -= old_ids
        if ids:
            result = await self.db.spectra.insert_many((
                {'ident': ident, 'label': -1} for ident in ids
                ))
            self.redirect(self.reverse_url('classification'))


class SpectraHandler(BaseHandler):
    async def get(self, kind):
        """Display spectra."""
        if kind == 'all':
            query = {'label': {'$gt': -1}}
        elif kind == 'emission':
            query = {'label': {'$eq': 0}}
        elif kind == 'absorption':
            query = {'label': {'$eq': 1}}
        elif kind == 'unknown':
            query = {'label': {'$eq': 2}}

        spectra = []
        async for spectrum in self.db.spectra.find(query):
            spectra.append(spectrum)

        self.render('show-spectra.html',
            heading=kind.capitalize() + ' Spectra',
            spectra=spectra
        )


class IndexHandler(BaseHandler):
    async def get(self):
        coll = self.db.spectra
        counts = []
        counts.append({
            'name': 'unclassified',
            'value': await coll.find({'label': {'$eq': -1}}).count()
        })
        counts.append({
            'name': 'emission',
            'value': await coll.find({'label': {'$eq': 0}}).count()
        })
        counts.append({
            'name': 'absorption',
            'value': await coll.find({'label': {'$eq': 1}}).count()
        })
        counts.append({
            'name': 'unknown',
            'value': await coll.find({'label': {'$eq': 2}}).count()
        })
        self.render('index.html', counts=counts)


class SpectrumHandler(BaseHandler):
    async def get(self, spectrum_id):
        """Display a spectrum."""
        ident = {'_id': ObjectId(spectrum_id)}
        spectrum = await self.db.spectra.find_one(ident)
        self.render('spectrum.html', spectrum=spectrum)

    async def post(self, spectrum_id):
        label = self.get_argument('label')
        label_dict = {'label': 2}   # default is unknown
        if label == 'emission':
            label_dict['label'] = 0
        elif label == 'absorption':
            label_dict['label'] = 1

        ident_dict = {'_id': ObjectId(spectrum_id)}
        await self.db.spectra.update_one(ident_dict, {'$set': label_dict})
        self.redirect(self.reverse_url('spectrum', spectrum_id))


class SpectrumAPIHandler(BaseHandler):
    async def get(self, spectrum_id):
        ident = {'_id': ObjectId(spectrum_id)}
        spectrum = await self.db.spectra.find_one(ident)
        try:
            wave, flux = spectrum['wave'], spectrum['flux']
        except KeyError:
            fits_dict = download_fits(spectrum['ident'])
            result = await self.db.spectra.update_one(ident, {'$set': fits_dict})
            spectrum = await self.db.spectra.find_one(ident)
            wave, flux = spectrum['wave'], spectrum['flux']
        data = {'data': [
            {'wave': w, 'flux': f} for w, f in zip(wave, flux) if 6500 <= w <= 6600
        ]}
        self.write(data)


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
        # parse command line arguments here so when testing with pytest
        # it is possible to provide database information
        parse_command_line()
        handlers = [
            URLSpec(r'/', IndexHandler, name='index'),
            URLSpec(r'/spectra/(all|absorption|emission|unknown)', SpectraHandler, name='spectra'),
            URLSpec(r'/spectra/([0-9a-z]+)', SpectrumHandler, name='spectrum'),
            URLSpec(r'/login', LoginHandler, name='login'),
            URLSpec(r'/logout', LogoutHandler, name='logout'),
            URLSpec(r'/classification/export', ExportHandler, name='export'),
            URLSpec(r'/classification', ClassificationHandler, name='classification'),
            URLSpec(r'/classification/classify', ClassifyHandler, name='classify'),
            # API
            URLSpec(r'/api/spectra/([0-9a-z]+)', SpectrumAPIHandler, name='api_spectrum'),
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

        self.db = motor.MotorClient(options.db).spectalview
        self.db.users.insert_one({'username': 'admin', 'password': 'default'})
