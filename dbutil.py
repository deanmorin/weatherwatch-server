import ast
import locale
import redisinstance as redis
from accuracy import ACCURACY_TEST_LOCATIONS

def all_locations():
    siteCodes = ast.literal_eval(redis.db.get('site_codes'))
    locations = siteCodes.keys()

    locale.setlocale(locale.LC_ALL, "")
    locations.sort(cmp=locale.strcoll) 

    return locations


def previous_days(location):
    key = 'loc:' + location + ':prev_days'
    prev = redis.db.lrange(key, 0, 1)
    return prev


def old_fcast_locs():
    return ACCURACY_TEST_LOCATIONS


def old_forecasts(location):
    key = 'forecast:' + location
    fcast = redis.db.lrange(key, 0, 4)
    return fcast
