from redis import Redis

if __debug__:
    db = Redis(host='localhost', db=0)
else:
    db = Redis(host='localhost', db=1)
test = Redis(host='localhost', db=2)
