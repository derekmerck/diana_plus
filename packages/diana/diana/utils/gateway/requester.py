import logging
import requests
import attr

# Diana-agnostic HTTP Gateways

@attr.s
class Requester(object):
    host = attr.ib()
    port = attr.ib()
    auth = attr.ib(init=False, default=None)
    path = attr.ib(default=None)
    protocol = attr.ib(default="http")

    def _url(self, resource):
        if self.path:
            return "{}://{}:{}/{}/{}".format(self.protocol, self.host, self.port, self.path, resource)
        else:
            return "{}://{}:{}/{}".format(self.protocol, self.host, self.port, resource)

    def _return(self, response):
        if not response.status_code == 200:
            raise requests.ConnectionError
        elif response.headers.get('content-type').find('application/json') >= 0:
            return response.json()
        else:
            return response.content

    def _get(self, url, params=None, headers=None, auth=None):
        r = requests.get(url, params=params, headers=headers, auth=auth)
        return self._return(r)

    def _put(self, url, data=None, headers=None, auth=None):
        r = requests.put(url, data=data, headers=headers, auth=auth)
        return self._return(r)

    def _post(self, url, data=None, headers=None, auth=None):
        r = requests.post(url, data=data, headers=headers, auth=auth)
        return self._return(r)

    def _delete(self, url, headers=None, auth=None):
        r = requests.delete(url, headers=headers, auth=auth)
        return self._return(r)

    def get(self, resource, params=None):
        raise NotImplementedError

    def put(self, url, data=None):
        raise NotImplementedError

    def post(self, resource, data=None):
        raise NotImplementedError

    def delete(self, url):
        raise NotImplementedError
