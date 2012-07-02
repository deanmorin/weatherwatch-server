import ast
from flask import Markup

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
