from tornado.httputil import url_concat
import xml.etree.ElementTree as ET


def make_ssap_url(url, band, request='queryData', file_format='votable',
    maxrec=10 ** 6, url_parameters={}):
    url_parameters['BAND'] = str(band)
    url_parameters['REQUEST'] = request
    url_parameters['FORMAT'] = file_format
    url_parameters['MAXREC'] = maxrec
    return url_concat(url, url_parameters)

def get_ids(ssap_xml):
    root = ET.fromstring(ssap_xml)
    # first RESOURCE
    # last TABLE
    # last DATA
    # first TABLEDATA
    # eleventh ID
    return (c[11].text for c in root[0][-1][-1][0])
