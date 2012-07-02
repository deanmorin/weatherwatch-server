import ast
import locale
import redisinstance as redis

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
