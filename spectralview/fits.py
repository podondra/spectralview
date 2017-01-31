from astropy.io import fits
import numpy as np

def parse_fits(file):
    with fits.open(file) as hdulist:
        # TODO
        # need to copy the data else it file pointer
        # won't be realesed and exception would be raised
        name = hdulist[0].header['object']
        wave = hdulist[1].data.field(0).tolist()
        flux = hdulist[1].data.field(1).tolist()
    return {
            'name': name,
            'wave': wave,
            'flux': flux
            }
