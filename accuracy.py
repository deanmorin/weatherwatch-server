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


def temp():
    locations = [ 'Squamish', 'Vancouver', 'Penticton', 'Banff' ]

    for loc in locations:
        url = location_url(redis=redis.test, locName=loc)
        xml = xp.xml_from_url(url, 'latin_1')

        date, forcasts = forecasts(xml, 5)

        #redis.devel.
