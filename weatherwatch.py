from flask import Flask, flash, g, make_response, redirect, render_template, \
     request, url_for
from redis import Redis
import redisinstance as redis

# configuration
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
    print 'before'
    redis.devel.incr('visits')

@app.after_request
def after_request(response):
    print 'after'
    return response

@app.route('/')
def index():
    location = request.cookies.get('location')
    response = make_response(render_template('index.html'))
    response.set_cookie('location', 'here')
    return response

@app.route('/recap/', methods=['POST'])
def recap():
    flash(request.form['location'])
    return redirect(url_for('index'))

@app.route('/<int:longitude>/<int:latitude>/')
def precipitation(longitude, latitude):
    precip = 33
    return '%dmm' % precip

@app.route('/locations/', methods=['POST'])
def locations():
    flash(locations_in_region(None))
    return redirect(url_for('index'))

def locations_in_region(region):
    locations = []
    locations.append('Tofino')
    locations.append('Cranbrook')
    return locations

if __name__ == '__main__':
    with app.test_request_context():
        print url_for('precipitation', longitude=20, latitude=20)
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0')
