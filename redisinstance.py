from redis import Redis

devel = Redis(host='localhost',  db=0)
live  = Redis(host='localhost',  db=1)
test  = Redis(host='localhost',  db=2)
