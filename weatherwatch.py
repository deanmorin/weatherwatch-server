from flask import Flask, flash, g, make_response, redirect, render_template, \
     request, url_for
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
    redis.db.incr('requests')
    return response

@app.route('/')
def index():
    prevLoc = request.cookies.get('location')
    locations = dbutil.all_locations()
    response = make_response(render_template('index.html',
            locations=locations, default=None))
    return response

@app.route('/recap/')
def recap():
    location = request.args.get('location')
    if location is not None:
        prev = dbutil.previous_days(location)
        prevStr = present.format_previous(prev)
        flash(prevStr)

    locations = dbutil.all_locations()
    response = make_response(render_template('index.html',
            locations=locations, default=location))
    response.set_cookie('location', 'here')
    return response

@app.route('/previous_forecasts/')
def previous_forecasts():
    location = request.args.get('fcast_location')
    #flash(locations_in_region(None))
    return redirect(url_for('index'))

if __name__ == '__main__':
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0')
