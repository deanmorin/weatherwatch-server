import sys
from lxml import etree
import redisinstance as redis
import xmlparsing as xp

def next_days(currentDay, numDays):
    days = [ 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 
             'Thursday', 'Friday', 'Saturday' ]
    nextDays = []
    i = days.index(currentDay)
    count = 0

    while count < numDays:
        i += 1
        if i == len(days):
            i = 0
        nextDays.append(days[i])
        count += 1
    
    return nextDays


def forecasts(xml, numDays):
    date = ''
    forecasts = []
    nextDays = None
    context = etree.iterparse(xml, events=('start',), tag='forecastGroup')

    if numDays > 5:
        numDays = 5
    i = 0

    forecastGroup = context.next()[1]

    for element in list(forecastGroup):

        if (element.tag == 'dateTime' 
                and element.attrib['name'] == 'forecastIssue'
                and element.attrib['zone'] != 'UTC'):

            year  = element.findtext('year')
            month = element.findtext('month')
            day   = element.findtext('day')
            dayName = element.find('day').attrib['name']

            if any(text is None for text in (year, month, day, dayName)):
                return None

            date = year + '-' + month + '-' + day
            nextDays = next_days(dayName, numDays)
            
        elif element.tag == 'forecast' and element.findtext('period') == nextDays[0]:
            forecasts.append({})

            temps = element.find('temperatures').findall('temperature')

            for t in temps:
                if t.attrib['class'] == 'high':
                    forecasts[i]['high'] = t.text
                elif t.attrib['class'] == 'low':
                    forecasts[i]['low'] = t.text

            pop = element.find('abbreviatedForecast').findtext('pop')
            if pop is None or pop == '':
                pop = '0'
            forecasts[i]['pop'] = pop

            i += 1
            nextDays.pop(0)
            
        if i == numDays:
            return date, forecasts

    return None, None


def main():
    usage = 'usage: python %s LIVE|devel' % (sys.argv[0])
    usage += "\n> note: python must be run with the '-O' switch to use the "
    usage += 'live database'

    if len(sys.argv) < 2:
        print usage
        exit()

    db = sys.argv[1]

    if (db == 'LIVE' and not __debug__) or (db == 'devel' and __debug__):
        r=redis.db
    else:
        print usage
        exit()

    locations = [ 'Squamish', 'Vancouver', 'Penticton', 'Banff' ]

    for loc in locations:
        url = xp.location_url(redis=r, locName=loc)
        xml = xp.xml_from_url(url)

        date, fcast = forecasts(xml, 5)

        if date is None or fcast is None:
            continue

        key = 'forecast:' + loc
        val = (date, fcast)

        lastRecord = r.lrange(key, 0, 0)

        if (lastRecord is not None and len(lastRecord) == 1 
                and lastRecord[0][0] == date):
            continue

        r.lpush(key, val)


if __name__ == '__main__':
    main()
