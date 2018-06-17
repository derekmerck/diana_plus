import logging
import attr
from ..apis import Orthanc, Redis
from .tasks import do


def star(func):
    def wrapper(self, *args, **kwargs):
        celery_args = {}
        if self.celery_queue:
            celery_args['queue'] = self.celery_queue
        if not kwargs:
            kwargs = {}
        kwargs['pattern'] = self.pattern
        kwargs['method'] = func.__name__
        # logging.warning("wrapper: {}".format(kwargs))
        return do.apply_async(args, kwargs, **celery_args)
    return wrapper


@attr.s
class DistribMixin(object):
    celery_queue = attr.ib(default='default')

    @star
    def get(self, id, **kwargs):
        pass

    @star
    def put(self, item, **kwargs):
        pass

    @star
    def handle(self, item, **kwargs):
        pass



@attr.s
class Orthanc(DistribMixin, Orthanc):
    pass


@attr.s
class Redis(DistribMixin, Redis):
    pass