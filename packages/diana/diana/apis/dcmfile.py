import os
import attr
from .dixel import Dixel
from ..utils import DicomLevel, Pattern, gateway

@attr.s
class DicomFile(Pattern):
    location = attr.ib( default=None )
    gateway = attr.ib( init=False )

    @gateway.default
    def set_dfio(self):
        return gateway.DicomFile(location=self.location)

    def put(self, item, path=None, explode=None):
        fn = item.meta['FileName']
        data = item.data

        if item.level == DicomLevel.INSTANCES and \
                os.path.splitext(fn)[-1:] != ".dcm":
            fn = fn + '.dcm'   # Single file
        if item.level > DicomLevel.INSTANCES and \
            os.path.splitext(fn)[-1:] != ".zip":
            fn = fn + '.zip'   # Archive format

        self.dfio.write(fn, data, path=path, explode=explode )

    def get(self, fn, path=None, pixels=False, file=False):
        # print("getting")
        dcm, fp = self.dfio.read(fn, path=path, pixels=pixels)

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
        if pixels:
            _pixels = dcm.pixel_array

        _file = None
        if file:
            with open(fp, 'rb') as f:
                _file = f.read()

        item = Dixel(level=DicomLevel.INSTANCES, meta=_meta, pixels=_pixels, file=_file)
        return item
