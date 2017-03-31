import io
from astropy.io import fits
import numpy as np
from tornado.httputil import url_concat
import tornado.httpclient as httpclient
import spectralview.utils as utils


def parse_fits(filename):
    with fits.open(filename) as hdulist:
        try:
            name = hdulist[1].header['object']
        except KeyError:
            name = 'unknown'
        wave = hdulist[1].data.field(0).tolist()
        flux = hdulist[1].data.field(1).tolist()
    return {
        'name': name,
        'wave': wave,
        'flux': flux
    }

def make_datalink_url(ident, fluxcalib='normalized',
    lambda_min=6282e-10, lambda_max=6733e-10,
    file_format='application/fits',
    url='http://vos2.asu.cas.cz/ccd700/q/sdl/dlget'
):
    url_parameters = {
        'ID': ident,
        'FLUXCALIB': fluxcalib,
        'BAND': str(lambda_min) + ' ' + str(lambda_max),
        'FORMAT': file_format,
    }
    return url_concat(url, url_parameters)

def download_fits(ident):
    url = make_datalink_url(ident)
    # TODO try Exception
    response = utils.request_url(make_datalink_url(ident))
    if response:
        return parse_fits(io.BytesIO(response.body))
    return None
