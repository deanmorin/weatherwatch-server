import ast
import dbutil
from flask import make_response, Markup, render_template

def provide_dropdowns(recapDefault=None, fcastDefault=None):
    recapLocations = dbutil.all_locations()
    fcastLocations = dbutil.old_fcast_locs()
    response = make_response(render_template('index.html',
            recapLocations=recapLocations, fcastLocations=fcastLocations,
            recapDefault=recapDefault, fcastDefault=fcastDefault))
    return response


def format_previous(prev):
    prevStr = ''

    if len(prev) == 0:
        prevStr += 'No data available for this location'

    i = 1
    plural = ''

    for day in prev:
        day = ast.literal_eval(day)

        if (i > 1):
            plural = 's'

        prevStr += '<div>%d Day%s Ago: High: %s  Low: %s  Precip: %s</div>' \
                % (i, plural, day['high'], day['low'], day['precip'])
        i += 1

    if len(prev) == 1:
        prevStr += 'Two Days Ago: data not yet available'

    return Markup(prevStr)


def format_forecasts(fcasts):
    fcastStr = ''

    if len(fcasts) == 0:
        prevStr += 'No forecasts available for this location'

    # TODO: provide a better interface for viewing forecasts; currently only
    # the most recent day's forecasts are available

    for day in fcasts:
        dayTuple = ast.literal_eval(day)
        date = dayTuple[0]
        fcastStr += '<div>Recorded on %s</div>' % (date)
        i = 1

        fcastGroup = dayTuple[1]

        for f in fcastGroup:
            if 'high' in f:
                high = f['high']
            else:
                high = '&nbsp-$nbsp'

            if 'low' in f:
                low = f['low']
            else:
                low = '&nbsp-&nbsp'

            # pop is always present
            pop = f['pop']

            fcastStr += '<div>%d Day Forecast - High: %s Low: %s POP: %s</div>' \
                     %  (i, high, low, pop)
            i += 1

        break

    return Markup(fcastStr)
