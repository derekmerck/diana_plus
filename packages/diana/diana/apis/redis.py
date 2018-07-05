# Data cache

import logging
from uuid import UUID
from typing import Union, Iterable
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

    @classmethod
    def item2str(cls, item: Union[Dixel, UUID, str]) -> str:
        if type(item) == Dixel:
            id = str( item.uid )
        elif type(item) == UUID:
            id = str(item)
        elif type(item) == str:
            id = item
        else:
            raise ValueError("Can not convert type {} to key str!".format(type(item)))
        return id

    def get(self, item: Union[Dixel, UUID, str], **kwargs):

        id = Redis.item2str( item )
        item = loads( self.gateway.get(id) )
        return item

    def remove(self, item: Union[Dixel, UUID, str] ):

        id = Redis.item2str(item)
        self.gateway.delete(id)

    def put(self, item: Dixel) -> Dixel:

        id = Redis.item2str(item)
        self.gateway.set( id, dumps(item) )
        return item

    def sput(self, sid: str, items: Iterable):
        for item in items:
            self.sadd(sid, item)

    def sget(self, sid: str):
        result = set()
        for iid in self.gateway.smembers(sid):
            item = self.get(iid)
            result.add(item)
        return result

    def sadd(self, sid, item):
        self.gateway.sput(sid, Redis.item2str(item))
        self.put(item)

    def sremove(self, sid, iid):
        self.gateway.srem(sid, iid)


