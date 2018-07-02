import logging
import requests
import attr
from typing import Mapping

# Diana-agnostic HTTP Gateways

# TODO: Turn ssl verification on

@attr.s
class Requester(object):
    host = attr.ib()
    port = attr.ib()
    auth = attr.ib(init=False, default=None)
    path = attr.ib(default=None)
    protocol = attr.ib(default="http")

    def _url(self, resource: str=''):
        if self.path:
            return "{}://{}:{}/{}/{}".format(self.protocol, self.host, self.port, self.path, resource)
        else:
            return "{}://{}:{}/{}".format(self.protocol, self.host, self.port, resource)

    def _return(self, response: requests.Response):
        if response.status_code < 200 or response.status_code > 299:
            logging.error(response)
            raise requests.ConnectionError( response )

        elif response.headers.get('content-type').find('application/json') >= 0:
            return response.json()

        else:
            return response.content

    def _get(self, url: str, params: Mapping=None, headers: Mapping=None, auth=None):
        r = requests.get(url, params=params, headers=headers, auth=auth, verify=False)
        return self._return(r)

    def _put(self, url: str, data=None, headers: Mapping=None, auth=None):
        r = requests.put(url, data=data, headers=headers, auth=auth, verify=False)
        return self._return(r)

    def _post(self, url: str, params: Mapping=None, data=None, json: Mapping=None, headers: Mapping=None, auth=None):
        r = requests.post(url, params=params, data=data, json=json, headers=headers, auth=auth, verify=False)
        return self._return(r)

    def _delete(self, url: str, headers: Mapping=None, auth=None):
        r = requests.delete(url, headers=headers, auth=auth, verify=False)
        return self._return(r)

    def get(self, resource: str, params: Mapping=None):
        raise NotImplementedError

    def put(self, url: str, data=None):
        raise NotImplementedError

    def post(self, resource: str, data=None):
        raise NotImplementedError

    def delete(self, url: str):
        raise NotImplementedError
