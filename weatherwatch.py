from flask import Flask, flash, request
from redis import Redis
import dbutil
import present
import redisinstance as redis

# configuration
if __debug__:
    DEBUG = True
SECRET_KEY = '\x15SPi\xfd\x15\x01\x15\xf8\xc4\xa5\xe8\xe8\xf8!\x87\x99c\x98\x9e\x97\xa7u5'

app = Flask(__name__)
app.config.from_object(__name__)

@app.after_request
def after_request(response):
    """Count the total number of requests."""
    redis.db.incr('requests')
    return response


@app.route('/')
def index():
    """Main entry point to the webapp."""
    last = request.cookies.get('last')

    if last is not None:
        lastAction = last.split(',')
        print lastAction

        if lastAction[0] == 'recap':
            response = present.provide_dropdowns(recapDefault=lastAction[1])
        elif lastAction[0] == 'fcast':
            response = present.provide_dropdowns(fcastDefault=lastAction[1])
    else:
        response = present.provide_dropdowns()

    print response
    print last
    return response


@app.route('/recap/')
def recap():
    """Show previous days' values in 'flash' area."""
    location = request.args.get('location')
    if location is not None:
        prev = dbutil.previous_days(location)
        prevStr = present.format_previous(prev)
        flash(prevStr)

    response = present.provide_dropdowns(recapDefault=location)
    response.set_cookie('last', ('recap,' + location))
    return response


@app.route('/previous_forecasts/')
def previous_forecasts():
    """Show previous forecasts in 'flash' area."""
    location = request.args.get('fcast_location')
    if location is not None:
        fcast = dbutil.old_forecasts(location)
        fcastStr = present.format_forecasts(fcast)
        flash(fcastStr)

    response = present.provide_dropdowns(fcastDefault=location)
    response.set_cookie('last', 'fcast,' + location)
    return response


if __name__ == '__main__':
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0')
