
from diana.apis import Dixel
from diana import apis as local_apis
from diana.star import apis as star_apis
import logging

logging.basicConfig(level=logging.DEBUG)

d = Dixel()
d_id = d.id

logging.info("Testing local apis")
cache = local_apis.Redis()
cache.put(d)
e = cache.get(d_id)

assert d == e

logging.info("Testing distributed apis")
cache.put(d)
cache = star_apis.Redis()
f = cache.get(d_id).get()

assert d == f