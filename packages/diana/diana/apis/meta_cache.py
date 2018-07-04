"""
Reads dixel meta and reports from or writes to a csv file
"""

from csv import DictReader, DictWriter
from typing import Union, Mapping
import attr
from diana.utils import Pattern, DicomLevel
from .dixel import Dixel


# Doesn't really need to be patternable
@attr.s
class MetaCache(Pattern):
    location = attr.ib( default=None )
    cache = attr.ib( init=False, factory=dict )
    fieldnames = attr.ib( init=False, default=[] )

    montage_keymap = {
        "Accession Number": "AccessionNumber",
        "Report Text": "_report"
    }

    def get(self, item: Union[Dixel, str], **kwargs):

        # Get needs to accept oid's or items with oid's
        if type(item) == Dixel:
            id = item.id
        elif type(item) == str:
            id = item
        else:
            raise ValueError("Can not get type {}!".format(type(item)))

        meta = self.cache.get( id )
        level = meta["_level"]
        del(meta["_level"])

        if meta.get('_report'):
            report = meta['report']
        else:
            report = None

        item = Dixel( id=id, meta=meta, level=level, report=report )
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
        self.cache[item.id] = meta

    def load(self, key_field="AccessionNumber", level=DicomLevel.STUDIES, keymap: Mapping=None):

        def remap_keys(item):
            for k,v in keymap:
                if item.get(k):
                    item[v] = item[k]
                    del( item[k] )
            return item

        def remap_fields(fieldnames):
            return [keymap.get(f) or f for f in fieldnames]

        with open(self.location) as f:
            reader = DictReader(f)
            self.fieldnames = remap_fields( reader.fieldnames )

            for item in reader:
                key = item[key_field]
                if not item.get("_level"):
                    item["_level"] = level

                self.cache[key] = remap_keys(item)

    def dump(self, fp=None, fieldnames=None):
        fp = fp or self.location
        fieldnames = fieldnames or self.fieldnames
        if "_level" not in fieldnames:
            fieldnames.append("_level")

        with open(fp, "w") as f:
            writer = DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.cache)

    def __iter__(self):
        self.iterator = self.cache.keys()

    def __next__(self):
        yield self.get(next(self.iterator))

