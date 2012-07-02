import os
import sys
import tempfile
import unittest
sys.path.insert(0, '../')
import weatherwatch as ww

class WeatherWatchTestCase(unittest.TestCase):

    def setUp(self):
        ww.app.config['TESTING'] = True
        self.app = ww.app.test_client()
        #print 'su'

    def tearDown(self):
        pass
        #print 'td'

    def test_empty_db(self):
        rv = self.app.get('/', follow_redirects=True)
        assert '<input' in rv.data

    def test_recap(self):
        rv = self.app.post('/recap/', data=dict(
                location='3'), follow_redirects=True)
        assert '3' in rv.data

if __name__ == '__main__':
    unittest.main()
