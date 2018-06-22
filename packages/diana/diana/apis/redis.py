# Data cache

import logging
from typing import Union
import attr
from dill import dumps, loads
from redis import Redis as RedisGateway
from diana.utils import Pattern
from .dixel import Dixel

@attr.s
class Redis(Pattern):
    host = attr.ib( default="localhost" )
    port = attr.ib( default="6379" )
    password = attr.ib( default="passw0rd!" )
    db = attr.ib( default=0 )
    gateway = attr.ib( init=False )

    @gateway.default
    def connect(self):
        return RedisGateway(host=self.host, port=self.port, db=self.db, password=self.password)

    def get(self, item: Union[Dixel, str], **kwargs):

        # Get needs to accept oid's or items with oid's
        if type(item) == Dixel:
            id = item.id
        elif type(item) == str:
            id = item
        else:
            raise ValueError("Can not get type {}!".format(type(item)))

        item = loads( self.gateway.get(id) )
        return item

    def put(self, item, **kwargs):
        self.gateway.set( item.id, dumps(item) )

