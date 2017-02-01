import spectralview.app
from tornado.testing import AsyncHTTPTestCase 

class TestSpectralViewApp(AsyncHTTPTestCase):
    def get_app(self):
        return spectralview.app.Application()

    def test_get_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
