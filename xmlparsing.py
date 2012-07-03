import ast
import requests
import sys
from io import BytesIO
from lxml import etree
import redisinstance as redis
from StringIO import StringIO

ENVCAN_URL = 'http://dd.weatheroffice.gc.ca'
FORECAST_URL = ENVCAN_URL + '/citypage_weather/xml'
SITE_LIST_URL = FORECAST_URL + '/siteList.xml'

def xml_from_url(url):
    """Returns a properly encoded bytes stream object to process the xml
       pointed to by 'url'.
    """
    r = requests.get(url)
    r.encoding = 'cp1252'
    xml = BytesIO(r.text.encode('cp1252'))
    return xml


def location_url(redis=None, locName=None, urlInfo=None):
    """Returns the URL for a given location's xml document.

    The URL can be constructed by either passing in both 'redis' and 'locName'
    or 'urlInfo' by itself.

    redis -- Even though redis is used globally, this is passed in so that a
            test database can be used for unit tests.
    locName -- The location in question.
    urlInfo -- Info needed to make up the URL.
    """
    if urlInfo is None and redis is not None and locName is not None:
        siteCodes = ast.literal_eval(redis.get('site_codes'))
        urlInfo = siteCodes[locName]

    url = FORECAST_URL + '/' + str(urlInfo[0]) + '/' + str(urlInfo[1]) + '_e.xml'
    return url


def yesterday_conditions(xml):
    """Returns the actual recorded values from the previous day, as well as the
       date that they were retrieved.

    xml -- The document containing the previous day's info.
    """
    yesterday = {}
    context = etree.iterparse(xml, events=('start',))

    # TODO skip child elements when parent doesn't match conditions below
    for event, element in context:
        if (element.tag == 'dateTime' 
                and element.attrib['name'] == 'xmlCreation'
                and element.attrib['zone'] != 'UTC'):

            year  = element.findtext('year')
            month = element.findtext('month')
            day   = element.findtext('day')

            if any(text is None for text in (year, month, day)):
                return None

            yesterday['date_retrieved'] = year + '-' + month + '-' + day

        elif element.tag == 'yesterdayConditions':
            for child in element:

                if child.tag == 'temperature' and child.attrib['class'] == 'high':
                    yesterday['high'] = child.text
                elif child.tag == 'temperature' and child.attrib['class'] == 'low':
                    yesterday['low'] = child.text
                elif child.tag == 'precip':
                    yesterday['precip'] = child.text

            if all(value is None for value in (yesterday['high'],
                    yesterday['low'], yesterday['precip'])):
                return None

    return yesterday


def site_list_urls(xml):
    """Returns a dictionary with all of the locations as keys, and the info
       necessary to find their XML files.

    xml -- The Environment Canada site list document.
    """
    # TODO use 'fast iterparse' www.ibm.com/developerworks/xml/library/x-hiperfparse/
    locations = {}
    context = etree.iterparse(xml, events=('start',))
    
    for event, element in context:
        if element.tag == 'site':
            name = element.findtext('nameEn')
            prov = element.findtext('provinceCode')
            code = element.attrib['code']

            if any(x is None for x in (name, prov, code)):
                # TODO find out why this fails on occasion
                pass
            else:
                locations[name] = (prov, code)
    
    return locations


def db_add_locations(redis, locations):
    """Adds all of the locations to the database.

    redis -- Even though redis is used globally, this is passed in so that a
            test database can be used for unit tests.
    locations -- A dictionary with all of the locations.
    """
    redis.set('site_codes', locations)


def insert_yesterday(redis, location, yesterday):
    """Inserts the previous day's values for a location into the database.

    redis -- Even though redis is used globally, this is passed in so that a
            test database can be used for unit tests.
    location -- The location in question.
    yesterday -- The previous day's values.
    """
    newRecord = True
    key = 'loc:' + location + ':prev_days'
    lastRecord = redis.lrange(key, 0, 0)

    if lastRecord is not None and len(lastRecord) == 1:
        lastRecordDict = ast.literal_eval(lastRecord[0])

        if lastRecordDict['date_retrieved'] == yesterday['date_retrieved']:
            newRecord = False

    if newRecord:
        redis.lpush(key, yesterday)


def update_records(redis, localFile=None):
    """Update the site list info in the database, and get the latest
       'yesterday values'.

    redis -- Even though redis is used globally, this is passed in so that a
            test database can be used for unit tests.
    localFile -- Can be passed in for testing. This way a local file is used
            to update the site list records.
    """
    if localFile == None:
        siteListXML = xml_from_url(SITE_LIST_URL)
    else:
        siteListXML = localFile

    locations = site_list_urls(siteListXML)
    db_add_locations(redis, locations)

    for loc, urlInfo in locations.items():
        url = location_url(urlInfo=urlInfo)
        xml = xml_from_url(url)
        yesterday = yesterday_conditions(xml)

        if yesterday is not None:
            # yesterdays values are not provided for all areas
            insert_yesterday(redis, loc, yesterday)


def main():
    """Used to get the latest data for the database. Can be run as a cron
       job.
    """
    usage = 'usage: python %s LIVE|devel' % (sys.argv[0])
    usage += "\n> note: python must be run with the '-O' switch to use the "
    usage += 'live database'

    if len(sys.argv) < 2:
        print usage
        exit()

    db = sys.argv[1]

    if (db == 'LIVE' and not __debug__) or (db == 'devel' and __debug__):
        update_records(redis.db)
    else:
        print usage


if __name__ == '__main__':
    main()
