# DICOM node or proxy

import logging
from typing import Mapping, Sequence, Callable, Union
import attr
from diana.utils import DicomLevel, Pattern, gateway, dicom_clean_tags
from .dixel import Dixel


@attr.s
class Orthanc(Pattern):
    host = attr.ib( default="localhost" )
    port = attr.ib( default="8042" )
    path = attr.ib( default=None )
    user = attr.ib( default="orthanc" )
    password = attr.ib( default="orthanc" )
    gateway = attr.ib( init=False )
    domains = attr.ib( factory=dict )

    @gateway.default
    def connect(self):
        return gateway.Orthanc(host=self.host, port=self.port, path=self.path,
                               user=self.user, password=self.password)

    @property
    def location(self):
        return self.gateway._url()

    def add_domain(self, domain: str, callback_dest: str=None ):
        self.proxies[domain] = callback_dest

    def get(self, item: Union[str, Dixel], level: DicomLevel=DicomLevel.STUDIES, view: str="tags") -> Dixel:

        # Get needs to accept oid's or items with oid's
        if type(item) == Dixel:
            oid = item.oid()
            level = item.level
        elif type(item) == str:
            oid = item
        else:
            raise ValueError("Can not get type {}, perhaps you chained after a 'put'?".format(type(item)))

        logging.info("{}: getting {}".format(self.__class__.__name__, oid))

        if view=="instance_tags":
            result = self.get(oid, level, view="meta")
            oid = result['instances'][0]
            view = "tags"
            level = DicomLevel.INSTANCES
            # Now get tags as normal

        # print(oid)
        result = self.gateway.get_item(oid, level, view=view)
        if view == "tags":
            # We can clean tags and assemble a dixel
            result = dicom_clean_tags(result)
            item = Dixel(meta=result, level=level)
            return item
        elif view == "file":
            # We can assemble a dixel
            item = Dixel(meta={'oid': oid}, file=result, level=level)
            return item
        else:
            # Return the meta info or binary data
            return result

    def put(self, item: Dixel):
        logging.info("{}: putting {}".format(self.__class__.__name__, item.id))

        if item.level != DicomLevel.INSTANCES:
            logging.warning("Can only 'put' Dicom instances.")
            raise ValueError
        if not item.file:
            logging.warning("Can only 'put' file data.")
            raise KeyError
        result = self.gateway.put_item(item.file)

        if not result:  # Success!
            return item
        else:
            return result

    # Handlers

    def anonymize(self, item: Dixel, replacement_map: Callable[[dict],dict]=None, remove: bool=False) -> Dixel:
        replacement_dict = replacement_map(item.meta)
        result = self.gateway.anonymize(item.oid, item.level, replacement_dict=replacement_dict)
        if remove:
            self.remove(item)
        return self.get( result['id'], level=item.level )

    def remove(self, item: Dixel):
        oid = item.oid()
        level = item.level
        return self.gateway.delete_item(oid, level)

    def find_item(self, item: Dixel, domain: str="local", retrieve: bool=False):
        """
        Have some information about a dixel, want to find the STUID, SERUID, INSTUID
        """

        def find_item_query(item):
            # Usually want to mask the dixel data to just AccessionNumber to isolate a study, or
            # AccessionNumber and SeriesDescription to isolate a series, if possible

            q = {}
            keys = {}

            # All levels have these
            keys[DicomLevel.STUDIES] = ['PatientID',
                                        'PatientName',
                                        'PatientBirthDate',
                                        'PatientSex',
                                        'StudyInstanceUID',
                                        'StudyDate',
                                        'StudyTime',
                                        'AccessionNumber']

            # Series level has these
            keys[DicomLevel.SERIES] = keys[DicomLevel.STUDIES] + \
                                      ['SeriesInstanceUID',
                                       'SeriesDescription',
                                       'ProtocolName',
                                       'SeriesNumber',
                                       'NumberOfSeriesRelatedInstances',
                                       'Modality']

            # For instance level, use the minimum
            keys[DicomLevel.INSTANCES] = ['SOPInstanceUID', 'SeriesInstanceUID']

            def add_key(q, key, dixel):
                q[key] = dixel.meta.get(key, '')
                return q

            for k in keys[item.level]:
                q = add_key(q, k, item)

            if item.level == DicomLevel.STUDIES and item.meta.get('Modality'):
                q['ModalitiesInStudy'] = item.meta.get('Modality')

            # logging.debug(pformat(q))

            query = {'Level': str(item.level),
                     'Query': q}

            return query

        query = find_item_query(item)

        if retrieve:
            retrieve_dest = self.domains[domain]
        else:
            retrieve_dest = None

        return self.gateway.find(query, domain, retrieve_dest=retrieve_dest)

    def send(self, item: Dixel, peer: str=None, modality: str=None):
        if modality:
            return self.gateway.send(item.id, item.level, modality_dest=modality)
        if peer:
            return self.gateway.send(item.id, item.level, peer_dest="peer")

    def clear(self, desc: str="all"):
        if desc == "all" or desc == "studies":
            self.inventory['studies'] = self.gateway.get("studies")
            for oid in self.inventory['studies']:
                self.gateway.delete_item(oid, DicomLevel.STUDIES)
        elif desc == "exports":
            self.gateway.do_delete("exports")
        elif desc == "changes":
            self.gateway.do_delete("changes")
        else:
            raise NotImplementedError

    def info(self):
        return self.gateway.statistics()
