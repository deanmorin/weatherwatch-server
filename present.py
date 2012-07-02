import ast
from flask import Markup

def format_previous(prev):
    prevStr = ''

    if len(prev) == 0:
        prevStr += 'No data available for this location'

    for day in prev:
        day = ast.literal_eval(day)

        if len(prev) > 0: 
            prevStr += '<div>One Day Ago: High: %s  Low: %s  Precip: %s</div>' \
                    % (day['high'], day['low'], day['precip'])
        if len(prev) > 1:
            prevStr += '<div>Two Days Ago: High: %s  Low: %s  Precip: %s</div>' \
                    % (day['high'], day['low'], day['precip'])
        else:
            prevStr += 'Two Days Ago: data not yet available'

    return Markup(prevStr)
