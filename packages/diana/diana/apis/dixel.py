
import attr
from ..utils import Pattern, DicomLevel, orthanc_id

@attr.s
class Dixel(Pattern):
    level = attr.ib(default=DicomLevel.STUDIES)
    meta = attr.ib(factory=dict)
    pixels = attr.ib(default=None)
    file = attr.ib(default=None)

    def oid(self, level=None):
        level = level or self.level

        if level == DicomLevel.PATIENTS:
            return orthanc_id(self.meta['PatientID'])
        elif level == DicomLevel.STUDIES:
            return orthanc_id(self.meta['PatientID'], self.meta['StudyInstanceUID'])
        elif level == DicomLevel.SERIES:
            return orthanc_id(self.meta['PatientID'], self.meta['StudyInstanceUID'],
                              self.meta['SeriesInstanceUID'])
        elif level == DicomLevel.INSTANCES:
            return orthanc_id(self.meta['PatientID'], self.meta['StudyInstanceUID'],
                              self.meta['SeriesInstanceUID'], self.meta['SOPInstanceUID'])
        else:
            raise ValueError("No such DICOM level: {}".format(level))



