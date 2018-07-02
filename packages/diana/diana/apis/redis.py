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

    def remove(self, item: Union[Dixel, str] ):

        if type(item) == Dixel:
            id = item.id
        elif type(item) == str:
            id = item
        else:
            raise ValueError("Can not remove type {}!".format(type(item)))

        self.gateway.delete(id)

    def put(self, item, **kwargs):
        self.gateway.set( item.id, dumps(item) )

    def sput(self, sid, set):
        for item in set:
            self.sadd(sid, item)

    def sget(self, id):
        result = set()
        for iid in self.gateway.smembers(id):
            item = self.get(iid)
            result.add(item)
        return result

    def sadd(self, sid, item):
        self.gateway.sput(id, item.id)
        self.put(item)

    def sremove(self, sid, iid):
        self.gateway.srem(sid, iid)


