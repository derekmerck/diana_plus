"""
Reads dixel meta and reports from or writes to a csv file
"""

from csv import DictReader, DictWriter
from typing import Union, Mapping
from dateutil import parser as dtparser
import attr
from diana.utils import Pattern, DicomLevel
from diana.utils.smart_encode import stringify
from .dixel import Dixel


# Doesn't really need to be patternable
@attr.s
class MetaCache(Pattern):
    location = attr.ib( default=None )
    cache = attr.ib( init=False, factory=dict )
    key_field = attr.ib( default="AccessionNumber" )

    montage_keymap = {
        "Accession Number": "AccessionNumber",
        "Patient MRN": "PatientID",
        "Patient First Name": 'PatientFirstName',
        "Patient Last Name": 'PatientLastName',

        'Patient Sex': 'PatientSex',
        'Patient Age': 'PatientAge',

        'Exam Completed Date': "StudyDate",
        'Organization': 'Organization',
        "Exam Code": "OrderCode",
        'Exam Description': 'StudyDescription',
        "Patient Status": "PatientStatus",
        'Ordered By': 'ReferringPhysicianName',

        "Report Text": "_report"
    }

    def get(self, item: Union[Dixel, str], **kwargs):

        # Get needs to accept oid's or items with oid's
        if type(item) == Dixel:
            id = item.uid
        elif type(item) == str:
            id = item
        else:
            raise ValueError("Can not get type {}!".format(type(item)))

        meta = self.cache.get( id )
        # self.logger.debug(meta)
        if type( meta.get("_level") ) == DicomLevel:
            level = meta.get("_level")
        else:
            level = DicomLevel.of( meta.get("_level" ) )

        report = meta.get('_report')
        uid    = meta.get('_uid')

        item = Dixel( uid=uid, meta=meta, level=level, report=report )
        return item

    def remove(self, item: Union[Dixel, str] ):

        if type(item) == Dixel:
            id = item.id
        elif type(item) == str:
            id = item
        else:
            raise ValueError("Can not remove type {}!".format(type(item)))

        if self.cache.get(id):
            del( self.cache[id] )

    def put(self, item, **kwargs):
        meta = item.meta
        meta['_level'] = item.level
        if item.report:
            meta['_report'] = item.report
        self.cache[meta[self.key_field]] = meta

    def load(self, fp: str=None, level=DicomLevel.STUDIES, keymap: Mapping=None):
        self.logger.debug("loading")
        fp = fp or self.location

        def remap_keys(item):
            ret = {}
            # Only take kv's that are in the remapper
            for k, v in keymap.items():
                vv = item.get(k)
                if vv:
                    ret[v] = vv
            return ret

        with open(fp) as f:
            reader = DictReader(f)

            for item in reader:
                if keymap:
                    item = remap_keys(item)
                if not item.get("_level"):
                    item["_level"] = level

                for k,v in item.items():
                    # if this k is a "date", normalize it
                    if k.lower().find("date") >= 0 or \
                            k.lower().find("dob") >= 0:
                        item[k] = dtparser.parse(v)


                # print(item)

                self.cache[item[self.key_field]] = item

    def dump(self, fp=None, fieldnames=None):
        self.logger.debug("dumping")
        fp = fp or self.location
        fieldnames = fieldnames or \
                     self.cache.values().__iter__().__next__().keys()

        # print(fieldnames)

        with open(fp, "w") as f:
            writer = DictWriter(f, fieldnames)
            writer.writeheader()
            for k, v in self.cache.items():
                for kk, vv in v.items():
                    out = stringify(vv)
                    if out:
                        v[kk] = out

                writer.writerow(v)

    def __iter__(self):
        # self.logger.debug("Setting iterator = cache.keys()")
        self.iterator = iter(self.cache.keys())
        return self

    def __next__(self):
        # self.logger.debug("Getting")
        return self.get(next(self.iterator))

