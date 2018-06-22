import os
from typing import Union
import attr
from .dixel import Dixel
from ..utils import DicomLevel, Pattern, gateway

@attr.s
class DicomFile(Pattern):
    location = attr.ib( default=None )
    gateway = attr.ib( init=False )

    @gateway.default
    def connect(self):
        return gateway.DicomFile(location=self.location)

    def put(self, item: Dixel, path: str=None, explode: str=None) -> Dixel:
        fn = item.meta['FileName']
        data = item.data

        if item.level == DicomLevel.INSTANCES and \
                os.path.splitext(fn)[-1:] != ".dcm":
            fn = fn + '.dcm'   # Single file
        if item.level > DicomLevel.INSTANCES and \
            os.path.splitext(fn)[-1:] != ".zip":
            fn = fn + '.zip'   # Archive format

        self.gateway.write(fn, data, path=path, explode=explode )
        return item

    def get(self, item: Union[str, Dixel], path: str=None, view: str="tags") -> Dixel:
        # print("getting")

        # Get needs to accept oid's or items with oid's
        if type(item) == Dixel:
            fn = item.meta['FileName']
        else:
            fn = item

        dcm, fp = self.gateway.read(fn, path=path, pixels=(view=="pixels"))

        _meta = {'PatientID': dcm[0x0010, 0x0020].value,
                 'AccessionNumber': dcm[0x0008, 0x0050].value,
                 'StudyInstanceUID': dcm[0x0020, 0x000d].value,
                 'SeriesInstanceUID': dcm[0x0020, 0x000e].value,
                 'SOPInstanceUID': dcm[0x0008, 0x0018].value,
                 'TransferSyntaxUID': dcm.file_meta.TransferSyntaxUID,
                 'TransferSyntax': str(dcm.file_meta.TransferSyntaxUID),
                 'MediaStorage': str(dcm.file_meta.MediaStorageSOPClassUID),
                 'PhotometricInterpretation': dcm[0x0028, 0x0004].value,  #MONOCHROME, RGB etc.
                 'FileName': fn,
                 'FilePath': fp}

        _pixels = None
        if view=="pixels":
            _pixels = dcm.pixel_array

        _file = None
        if view=="file":
            with open(fp, 'rb') as f:
                _file = f.read()

        item = Dixel(level=DicomLevel.INSTANCES, meta=_meta, pixels=_pixels, file=_file)
        return item
