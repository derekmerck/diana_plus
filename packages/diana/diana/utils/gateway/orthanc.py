# Diana-agnostic API for orthanc, no endpoint or dixel dependencies

import logging, json
import attr
from typing import Mapping
from .requester import Requester
from ..dicom import DicomLevel
from pprint import pprint

@attr.s
class Orthanc(Requester):
    user = attr.ib(default="orthanc")
    password = attr.ib(default="orthanc")
    auth = attr.ib(init=False)

    @auth.default
    def set_auth(self):
        return (self.user, self.password)

    # Wrapper for requester calls

    def get(self, resource: str, params=None):
        logging.debug("Getting {} from orthanc".format(resource))
        url = self._url(resource)
        return self._get(url, params=params, auth=self.auth)

    def put(self, resource: str, data=None):
        logging.debug("Putting {} into orthanc".format(resource))
        url = self._url(resource)
        return self._put(url, data=data, auth=self.auth)

    def post(self, resource: str, params=None, data=None, json: Mapping=None, headers: Mapping=None):
        logging.debug("Posting {} to orthanc".format(resource))
        url = self._url(resource)
        return self._post(url, params=params, data=data, json=json, auth=self.auth, headers=headers)

    def delete(self, resource: str):
        logging.debug("Deleting {} from orthanc".format(resource))
        url = self._url(resource)
        return self._delete(url, auth=self.auth)

    # item handling by oid and level

    def get_item(self, oid: str, level: DicomLevel, view: str):
        # View in [meta, tags, file*, image*, archive**]
        # * only instance level
        # * only series or study level

        params = None
        if view == "meta":
            postfix = None

        elif view == "tags":
            if level == DicomLevel.INSTANCES:
                postfix = "tags"
            else:
                postfix = "shared-tags"
            params = [("simplify", True)]

        elif view == "file" and level == DicomLevel.INSTANCES:
            postfix = "file"  # single dcm

        elif view == "image" and level == DicomLevel.INSTANCES:
            postfix = "preview"  # single dcm

        elif view == "archive" and level > DicomLevel.INSTANCES:
            postfix = "archive"   # zipped archive

        else:
            logging.error("Unsupported get view format {} for {}".format(view, level))
            return

        if postfix:
            resource = "{}/{}/{}".format(level, oid, postfix)
        else:
            resource = "{}/{}".format(level, oid)

        return self.get(resource, params)

    def put_item(self, file):
        resource = "instances"
        headers = {'content-type': 'application/dicom'}
        self.post(resource, data=file, headers=headers)

    def delete_item(self, oid: str, level: DicomLevel):
        resource = "{}/{}".format(level, oid)
        return self.delete(resource)

    def anonymize_item(self, oid: str, level: DicomLevel, replacement_map: Mapping=None):

        resource = "{}/{}/anonymize".format(level, oid)

        if replacement_map:
            replacement_json = json.dumps(replacement_map)
            data = replacement_json
            headers = {'content-type': 'application/json'}
            return self.post(resource, data=data, headers=headers)

        return self.post(resource)

    def find(self, query: Mapping, remote_aet: str, retrieve_dest: str=None):

        resource = 'modalities/{}/query'.format(remote_aet)
        headers = {"Accept-Encoding": "identity",
                   "Accept": "application/json"}

        r = self.post(resource, json=query, headers=headers)

        if not r:
            logging.warning("No reply from orthanc remote lookup")
            return

        qid = r["ID"]
        resource = 'queries/{}/answers'.format(qid)

        r = self.get(resource)

        if not r:
            logging.warning("No answers from orthanc lookup")
            return

        answers = r
        ret = []
        for aid in answers:
            resource = 'queries/{}/answers/{}/content?simplify'.format(qid, aid)
            r = self.get(resource)
            if not r:
                logging.warning("Bad answer from orthanc lookup")
                return
            ret.append(r)

            # If retrieve_dest defined, move data there (usually 1 study to here)
            if retrieve_dest:
                resource = 'queries/{}/answers/{}/retrieve'.format(qid, aid)
                headers = {'content-type': 'application/text'}
                rr = self.post(resource, data=retrieve_dest, headers=headers)
                logging.debug(retrieve_dest)
                logging.debug(rr)

        # Returns an array of answers
        return ret

    def send_item(self, oid: str, dest: str, dest_type):
        resource = "/{}/{}/send".format(dest_type, dest)
        data = oid
        headers = {'content-type': 'application/text'}
        self.post(resource, data=data, headers=headers)

    def statistics(self):
        return self.get("statistics")

