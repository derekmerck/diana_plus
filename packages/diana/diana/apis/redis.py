# Data cache

import logging
import attr
from diana.utils import Pattern
from dill import dumps, loads
from redis import Redis as RedisGateway

@attr.s
class Redis(Pattern):
    host = attr.ib( default="localhost" )
    port = attr.ib( default="6379" )
    path = attr.ib( default=None )
    # user = attr.ib( default="redis" )
    # password = attr.ib( default="redis" )
    db = attr.ib( default=0 )
    gateway = attr.ib( init=False )

    @gateway.default
    def connect(self):
        return RedisGateway(host=self.host, port=self.port, db=self.db)

    def get(self, id, **kwargs):
        item = loads( self.gateway.get(id) )
        return item

    def put(self, item, **kwargs):
        self.gateway.set( item.id, dumps(item) )

