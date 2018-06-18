import os
os.environ['DIANA_BROKER']="redis://:passw0rd!@localhost:6379/1"
os.environ['DIANA_RESULT']="redis://:passw0rd!@localhost:6379/2"

import logging
from diana.apis import Dixel
from diana import apis as local_apis
from diana.star import apis as star_apis

logging.basicConfig(level=logging.DEBUG)

d = Dixel()
d_id = d.id

logging.info("Testing local apis")
cache = local_apis.Redis(password="passw0rd!")
cache.put(d)
e = cache.get(d_id)

assert d == e

logging.info("Testing distributed apis")

cache.put(d)
cache = star_apis.Redis(host="192.168.1.102", password="passw0rd!")

for i in range(20):
    f = cache.get(d_id).get()
    assert d == f
