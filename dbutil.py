import ast
import locale
import redisinstance as redis
from accuracy import ACCURACY_TEST_LOCATIONS

def all_locations():
    """Returns a sorted list of all the locations in the database."""

    siteCodes = ast.literal_eval(redis.db.get('site_codes'))
    locations = siteCodes.keys()

    locale.setlocale(locale.LC_ALL, "")
    locations.sort(cmp=locale.strcoll) 

    return locations


def previous_days(location):
    """Returns the actual temperature and precipitation values recorded for the
       past two days.
    """
    key = 'loc:' + location + ':prev_days'
    prev = redis.db.lrange(key, 0, 1)
    return prev


def old_fcast_locs():
    """Returns a sorted list of locations. These were preselected for the
       comparison test.
    """
    fcast = ACCURACY_TEST_LOCATIONS
    fcast.sort()
    return fcast


def old_forecasts(location):
    """Returns all old forecasts for a location."""

    key = 'forecast:' + location
    fcast = redis.db.lrange(key, 0, 4)
    return fcast
