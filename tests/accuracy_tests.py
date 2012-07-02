# -*- coding: utf-8 -*-
import ast
import logging
import sys
import unittest
sys.path.insert(0, '../')
import redisinstance as redis
import accuracy
import xmlparsing

class AccuracyTestCase(unittest.TestCase):

    def setUp(self):
        redis.test.flushdb()
        requestsLog = logging.getLogger("requests")
        requestsLog.setLevel(logging.WARNING)

    def tearDown(self):
        pass

    def test_next_days(self):
        nextDays = accuracy.next_days('Monday', 1)
        assert len(nextDays) == 1
        assert nextDays.pop(0) == 'Tuesday'
        nextDays = accuracy.next_days('Thursday', 10)
        assert len(nextDays) == 10
        assert nextDays.pop(0) == 'Friday'
        assert nextDays.pop(0) == 'Saturday'
        assert nextDays.pop(0) == 'Sunday'
        assert nextDays.pop(0) == 'Monday'

    def test_forecasts(self):
        url = xmlparsing.location_url(redis=redis.db, locName='Victoria')
        xml = xmlparsing.xml_from_url(url)
        date, forecasts = accuracy.forecasts(xml, 7)
        assert date is not None and forecasts is not None
        # maximum allowed is 5 days
        assert len(forecasts) == 5

if __name__ == '__main__':
    unittest.main()
