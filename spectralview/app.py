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
from spectralview.fits import parse_fits, download_fits, query_flux_wave
import spectralview.utils as utils
import spectralview.ssap as ssap
from bson.objectid import ObjectId
from astropy.convolution import convolve, Gaussian1DKernel


# global dict with classes
# change the numbers with care
# do not include spaces in names
CLASSES = {
    'emission':      0,
    'absorption':    1,
    'unknown':       2, 
    'double-peak':   3,
}
INV_CLASSES = {
    v: k for k, v in CLASSES.items()
}
INV_CLASSES[-1] = 'unclassified'


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie('user')

    def my_render(self, template_name, **kwarg):
        self.render(template_name, classes=CLASSES, **kwarg)


class ExportHandler(BaseHandler):
    async def get(self):
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename=spectra.csv')
        self.write('id,label\n')
        async for spectrum in self.db.spectra.find({'label': {'$gt':-1}}):
            self.write(spectrum['ident'] + ',' + str(spectrum['label']) + '\n')
        self.finish()


class ClassifyHandler(BaseHandler):
    async def get(self):
        # TODO make function which download if not exist
        spectrum = await self.db.spectra.find_one({'label': -1})
        if spectrum == None:
            self.redirect(self.reverse_url('classification'))
        fits_dict = download_fits(spectrum['ident'])
        ident = {'_id': ObjectId(spectrum['_id'])}
        if fits_dict == None:
            result = await self.db.spectra.delete_many(ident)
            self.redirect(self.reverse_url('classify'))
        else:
            await self.db.spectra.update_one(ident, {'$set': fits_dict})
            spectrum = await self.db.spectra.find_one(ident)
            wave, flux = spectrum['wave'], spectrum['flux']
            self.my_render('classify.html', spectrum=spectrum)

    async def post(self):
        label = self.get_argument('label')
        label_dict = {'label': CLASSES[label]}
        ident_dict = {'_id': ObjectId(self.get_argument('ident'))}
        await self.db.spectra.update_one(ident_dict, {'$set': label_dict})
        self.redirect(self.reverse_url('classify'))


class ClassificationHandler(BaseHandler):
    async def get(self):
        spectra = []
        async for spectrum in self.db.spectra.find({'label': -1}):
            spectra.append(spectrum)
        self.my_render('classification.html', spectra=spectra)

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
        else:
            query = {'label': {'$eq': CLASSES[kind]}}

        spectra = []
        async for spectrum in self.db.spectra.find(query):
            spectra.append(spectrum)

        self.my_render('show-spectra.html',
            heading=kind.capitalize() + ' Spectra',
            spectra=sorted(spectra, key=lambda x: x['name'])
        )


class IntervalHandler(BaseHandler):
    async def get(self, kind, start, end):
        """Display spectra."""
        if kind == 'all':
            query = {'label': {'$gt': -1}}
        else:
            query = {'label': {'$eq': CLASSES[kind]}}

        spectra = []
        async for spectrum in self.db.spectra.find(query):
            spectra.append(spectrum)

        self.my_render('show-spectra.html',
            heading=kind.capitalize() + ' Spectra',
            spectra=sorted(spectra, key=lambda x: x['name'])[int(start):int(end)]
        )


class IndexHandler(BaseHandler):
    async def get(self):
        counts = [{
            'name': 'unclassified',
            'value': await self.db.spectra.find({'label': {'$eq': -1}}).count()
        }]
        # sort according to number assigned to a label
        for name, value in sorted(CLASSES.items(), key=lambda x: x[1]):
            counts.append({
                'name': name,
                'value': await self.db.spectra.find(
                    {'label': {'$eq': value}}
                ).count()
            })

        self.my_render('index.html', counts=counts)


class SpectrumHandler(BaseHandler):
    async def get(self, spectrum_id):
        """Display a spectrum."""
        collection = self.db.spectra
        spectrum = await query_flux_wave(collection, spectrum_id)
        self.my_render('spectrum.html', inv_classes=INV_CLASSES, spectrum=spectrum)

    async def post(self, spectrum_id):
        label = self.get_argument('label')
        label_dict = {'label': CLASSES[label]}
        ident_dict = {'_id': ObjectId(spectrum_id)}
        await self.db.spectra.update_one(ident_dict, {'$set': label_dict})
        self.redirect(self.reverse_url('spectrum', spectrum_id))


class SpectrumAPIHandler(BaseHandler):
    async def get(self, spectrum_id, interval):
        collection = self.db.spectra
        spectrum = await query_flux_wave(collection, spectrum_id)
        data = {}
        if interval == 'all':
            data = {'data': [
                {'wave': w, 'flux': f}
                for w, f in zip(spectrum['wave'], spectrum['flux'])
            ]}
        elif interval == 'halpha':
            data = {'data': [
                {'wave': w, 'flux': f}
                for w, f in zip(spectrum['wave'], spectrum['flux'])
                if 6500 <= w <= 6600
            ]}
        elif interval == 'convolved':
            gauss = Gaussian1DKernel(stddev=7)
            convolved = convolve(spectrum['flux'], gauss, boundary='extend')
            data = {'data': [
                {'wave': w, 'flux': f}
                for w, f in zip(spectrum['wave'], convolved)
                if 6500 <= w <= 6600
            ]}
        # response with Python's dict aka JSON
        self.write(data)


class LoginHandler(BaseHandler):
    def get(self):
        self.my_render('login.html', error=None)

    async def post(self):
        username = self.get_argument('username')
        user = await self.db.users.find_one({'username': username})
        if not user:
            self.my_render('login.html', error='user not found')
            return
        if self.get_argument('password') == user['password']:
            self.set_secure_cookie('user', username)
            self.redirect(self.reverse_url('index'))
        else:
            self.my_render('login.html', error='incorrect password')


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
            URLSpec(r'/spectra/(all|' + '|'.join(CLASSES) + ')', SpectraHandler, name='spectra'),
            URLSpec(r'/spectra/(all|' + '|'.join(CLASSES) + ')/([0-9]+)-([0-9]+)', IntervalHandler, name='interval'),
            URLSpec(r'/spectra/([0-9a-z]+)', SpectrumHandler, name='spectrum'),
            URLSpec(r'/login', LoginHandler, name='login'),
            URLSpec(r'/logout', LogoutHandler, name='logout'),
            URLSpec(r'/classification/export', ExportHandler, name='export'),
            URLSpec(r'/classification', ClassificationHandler, name='classification'),
            URLSpec(r'/classification/classify', ClassifyHandler, name='classify'),
            # API
            URLSpec(r'/api/spectra/([0-9a-z]+)/(all|halpha|convolved)', SpectrumAPIHandler, name='api_spectrum'),
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
