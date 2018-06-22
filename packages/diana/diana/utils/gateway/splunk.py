# Diana-agnostic API for splunk, no endpoint or dixel dependencies

# splunk-sdk does not support Python 3; this gateway provides a minimal
# replacement to find and put events

import time, logging, datetime, json
from pprint import pprint
from collections import OrderedDict
from typing import Mapping
import attr
from bs4 import BeautifulSoup
from .requester import Requester
from ..smart_encode import SmartJSONEncoder


@attr.s
class Splunk(Requester):
    hec_protocol = attr.ib( default="https" )
    hec_port = attr.ib( default="8089" )
    user     = attr.ib( default="admin" )
    password = attr.ib( default="splunk" )
    auth     = attr.ib( init=False )

    @auth.default
    def set_auth(self):
        return (self.user, self.password)

    # Wrapper for requester calls

    def get(self, resource: str, params=None):
        logging.debug("Getting {} from splunk".format(resource))
        url = self._url(resource)
        return self._get(url, params=params, auth=self.auth)

    def put(self, resource: str, data=None):
        logging.debug("Putting {} into splunk".format(resource))
        url = self._url(resource)
        return self._put(url, data=data, auth=self.auth)

    def post(self, resource: str, params=None, data=None, json: Mapping=None, headers: Mapping=None):
        logging.debug("Posting {} to splunk".format(resource))
        url = self._url(resource)
        return self._post(url, params=params, data=data, json=json, auth=self.auth, headers=headers)

    def delete(self, resource: str):
        logging.debug("Deleting {} from splunk".format(resource))
        url = self._url(resource)
        return self._delete(url, auth=self.auth)

    def find_events(self, q, timerange=None):

        if not timerange:
            earliest = "-1d"
            latest = "now"
        else:
            earliest = timerange.start.isoformat()
            latest = timerange.end.isoformat()

        # q = "search index=default".format("default")

        # q = 'search index="{index}" {query} | fields - _*'.format(index=index, query=query)

        response = self.post('services/search/jobs',
                             params={'earliest_time': earliest,
                                     'latest_time': latest},
                             data="search={0}".format(q))

        soup = BeautifulSoup(response, 'xml')  # Should have returned xml
        sid = soup.find('sid').string

        def poll_until_done(sid):
            isDone = False
            i = 0
            while not isDone:
                i = i + 1
                time.sleep(1)
                response = self.get('services/search/jobs/{0}'.format(sid),
                                    params={'output_mode': 'json'})
                isDone = response['entry'][0]['content']['isDone']
                status = response['entry'][0]['content']['dispatchState']
                if i % 5 == 1:
                    logging.debug('Waiting to finish {0} ({1})'.format(i, status))
            return response['entry'][0]['content']['resultCount']

        n = poll_until_done(sid)
        offset = 0
        result = []
        i = 0
        while offset < n:
            count = 50000
            offset = 0 + count*i
            response = self.get('services/search/jobs/{0}/results'.format(sid),
                                params={'output_mode': 'json',
                                        'count': count,
                                        'offset': offset})

            for r in response['results']:
                result.append( json.loads(r['_raw']) )
            i = i+1

        return result

    def put_event( self,
                   timestamp: datetime,
                   event: Mapping,
                   host: str,
                   index: str,
                   token: str ):

        if not timestamp:
            timestamp = datetime.datetime.now()

        def epoch(dt):
            tt = dt.timetuple()
            return time.mktime(tt)

        event_json = json.dumps(event, cls=SmartJSONEncoder)

        data = OrderedDict([('time', epoch(timestamp)),
                            ('host', host),
                            ('sourcetype', '_json'),
                            ('index', index ),
                            ('event', event_json )])

        def _hec_url() -> str:
            if self.path:
                return "{}://{}:{}/{}/services/collector/event". \
                    format(self.hec_protocol, self.host, self.hec_port, self.path)
            else:
                return "{}://{}:{}/services/collector/event". \
                    format(self.hec_protocol, self.host, self.hec_port)

        url = _hec_url()
        logging.debug("Posting to splunk hec")

        headers = {'Authorization': 'Splunk {0}'.format(token)}
        return self._post(url, json=data, headers=headers)




