import attr
from ..utils import Pattern, DicomLevel, orthanc_id


@attr.s(cmp=False, hash=None)
class Dixel(Pattern):
    level = attr.ib(default=DicomLevel.STUDIES)
    meta = attr.ib(factory=dict)
    pixels = attr.ib(default=None)
    file = attr.ib(default=None)

    def __hash__(self):
        try:
            return hash(self.oid())
        except:
            # If not enough info for oid, use the uid from Pattern
            return Pattern.__hash__(self)

    def oid(self, level: DicomLevel=None):

        # Stashed, may not be computable
        if not level and self.meta.get('oid'):
            return self.meta['oid']

        # Can compute any parent oid
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



