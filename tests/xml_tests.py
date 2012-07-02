# -*- coding: utf-8 -*-
import ast
import logging
import sys
import unittest
sys.path.insert(0, '../')
import redisinstance as redis
import xmlparsing

class XMLParsingTestCase(unittest.TestCase):

    def setUp(self):
        redis.test.flushdb()
        requestsLog = logging.getLogger("requests")
        requestsLog.setLevel(logging.WARNING)

    def tearDown(self):
        pass

    def test_site_list_urls(self):
        locations = xmlparsing.site_list_urls('testfiles/sitelistpartial.xml')
        assert locations[u'Pointe-à-la-Croix'] == ('QC', 's0000810')

        locations = xmlparsing.site_list_urls('testfiles/sitelist.xml')
        assert locations['Toronto Island'][0] == 'ON'
        assert locations['Toronto Island'][1] == 's0000785'
        
    def test_db_add_locations(self):
        locations = xmlparsing.site_list_urls('testfiles/sitelist.xml')
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
        loc = 'Îles-de-la-Madeleine'
        assert codesDict[loc] == ('QC', 's0000174')

    def test_yesterday_conditions(self):
        url = xmlparsing.FORECAST_URL + '/QC/s0000174_e.xml'
        xml = xmlparsing.xml_from_url(url)
        yesterday = xmlparsing.yesterday_conditions(xml)
        assert yesterday is not None

    def test_insert_yesterday(self):
        yesterday = { 'high': '32.7', 'precip': '0.0', 'low': '15.4',
                      'date_retrieved': '2012-07-02' }
        loc = u'Îles-de-la-Madeleine'
        xmlparsing.insert_yesterday(redis.test, loc, yesterday)
        key = 'loc:' + loc + ':prev_days'
        print redis.test.lrange(key, 0, 0)

    def test_update_records(self):
        xmlparsing.update_records(redis.test,
                                  localFile='testfiles/sitelistpartial.xml')
        xmlparsing.update_records(redis.test,
                                  localFile='testfiles/sitelistpartial.xml')
        # previous day info should only be inserted once per day
        assert redis.test.llen('loc:Athabasca:prev_days') == 1
        location = redis.test.lpop('loc:Athabasca:prev_days')
        locDict = ast.literal_eval(location)
        # shouldn't be more than 5 degrees higher/lower than historic extremes
        assert float(locDict['high']) < 45.0
        assert float(locDict['low']) > -68.0
        assert float(locDict['precip']) >= 0.0

        siteCodes = ast.literal_eval(redis.test.get('site_codes'))
        assert siteCodes[u'Pointe-à-la-Croix'] == ('QC', 's0000810')

    def test_location_url(self):
        xmlparsing.location_url(redis.db, locName='Squamish')

if __name__ == '__main__':
    unittest.main()
