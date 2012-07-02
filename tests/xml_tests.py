# -*- coding: utf-8 -*-
import ast
import logging
import os
import sys
import tempfile
import unittest
sys.path.insert(0, '../')
import redisinstance as redis
import xmlparsing

import time
class XMLParsingTestCase(unittest.TestCase):

    def setUp(self):
        redis.test.flushdb()
        requestsLog = logging.getLogger("requests")
        requestsLog.setLevel(logging.WARNING)

    def tearDown(self):
        pass

    def test_location_urls(self):
        assert not redis.test.get('Toronto Island')
        locations = xmlparsing.location_urls('testfiles/sitelist.xml')
        assert 'Toronto Island' in locations
        assert locations['Toronto Island'][0] == 'ON'
        assert locations['Toronto Island'][1] == 's0000785'

        
    def test_db_add_locations(self):
        locations = xmlparsing.location_urls('testfiles/sitelist.xml')
        f = open('testfiles/sitecodesdict.txt', 'w')
        f.write(str(locations))
        xmlparsing.db_add_locations(redis.test, locations)
        codes = redis.test.get('site_codes')
        f = open('testfiles/sitecodesdict.txt', 'r')
        # a failure here may just indicate that the codes have changed
        assert codes == f.read()
        codesDict = ast.literal_eval(codes)
        loc = 'Rivière-du-Loup'
        assert codesDict[loc] == ('QC', 's0000253')

    def test_yesterday_conditions(self):
        url = xmlparsing.FORECAST_URL + '/AB/s0000768_e.xml'
        xml = xmlparsing.xml_from_url(url, 'latin_1')
        yesterday = xmlparsing.yesterday_conditions(xml)
        assert yesterday is not None

    def test_update_records(self):
        xmlparsing.update_records(redis.test,
                                  localFile='testfiles/sitelistpartial.xml')
        xmlparsing.update_records(redis.test,
                                  localFile='testfiles/sitelistpartial.xml')
        # previous day info should only be inserted once 
        print redis.test.llen('loc:Athabasca:prev_days')
        assert redis.test.llen('loc:Athabasca:prev_days') == 1
        location = redis.test.lpop('loc:Athabasca:prev_days')
        locDict = ast.literal_eval(location)
        # shouldn't be more than 5 degrees higher/lower than historic extremes
        assert float(locDict['high']) < 45.0
        assert float(locDict['low']) > -68.0
        assert float(locDict['precip']) >= 0.0

if __name__ == '__main__':
    unittest.main()
