import json, time, collections
from pprint import pprint, pformat

from datetime import datetime
import attr
from splunklib import client, results
from .dixel import Dixel
from ..utils import Pattern
from ..utils.gateway.requester import Requester

@attr.s
class Splunk(Pattern):
    host = attr.ib( default="localhost" )
    port = attr.ib( default="8000" )
    user = attr.ib( default="splunk" )
    password = attr.ib( default="admin" )
    gateway = attr.ib( init=False )

    hec_port = attr.ib( default="8088" )
    hec_tok = attr.ib( factory=dict )
    hec_gateway = attr.ib( init=False )

    @gateway.default
    def connect(self):

        # Create a Service instance and log in
        gateway = client.connect(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password)

        # Print installed apps to the console to verify login
        for app in gateway.apps:
            self.logger.debug(app.name)

        return gateway

    @hec_gateway.default
    def connect_hec(self):
        return Requester(protocol="https", host=self.host, port=self.hec_port)


    def register_hec(self, name, token):
        self.hec_toks[name] = token


    def get(self, q, index=None, start=None, end=None, output_mode="json", **kwargs):

        def make_iso(value):
            if type(value) is type(datetime):
                return value.isoformat()

        kwargs.update( {"earliest_time": make_iso(start),
                        "latest_time": make_iso(end)} )

        q = 'search index="{index}" {q} | fields - _*'.format(index=index, q=q)

        r = self.gateway.jobs.oneshot(q, output_mode=output_mode, **kwargs)

        if output_mode == "json":
            data = json.loads(r.read())['results']
            self.logger.debug(pformat(data))
            r = set()
            for d in data:
                r.add( Dixel(meta=d, level=d['level']))

        return r


    def put(self, item, index="default", hec=None, host=None, sourcetype="_json"):

        def epoch(dt):
            tt = dt.timetuple()
            return time.mktime(tt)

        try:
            event_time = epoch(item['InstanceCreationDateTime'])
        except:
            event_time = epoch(datetime.now())

        # time _must_ be at front
        data = collections.OrderedDict([('time', event_time),
                                        ('host', host),
                                        ('sourcetype', sourcetype),
                                        ('index', index),
                                        ('event', item['meta'] )])
        # logging.debug(pformat(data))

        headers = {'Authorization': 'Splunk {0}'.format(self.hec_tok[hec])}
        url = self.hec_gateway._url('services/collector/event')

        self.hec_gateway._post(url, data=data, headers=headers)

