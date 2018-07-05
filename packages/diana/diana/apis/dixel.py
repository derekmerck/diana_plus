import logging
import attr
from dateutil import parser as dtparser
from .report import RadiologyReport
from ..utils import Pattern, DicomLevel, orthanc_id


@attr.s(cmp=False, hash=None)
class Dixel(Pattern):
    level = attr.ib(default=DicomLevel.STUDIES)
    meta  = attr.ib(factory=dict)
    pixels = attr.ib(default=None)
    file  = attr.ib(default=None)
    report = attr.ib(default=None, type=RadiologyReport)

    # Can't pickle a logger without dill, so Dixels don't need one
    logger = attr.ib(init=False, default=None)

    # Not always the best idea, can't put them in a set if the AN is identical
    def __hash__(self):

        try:
            return hash(self.AccessionNumber)
            # return hash(self.oid())
        except:
            # If not enough info for oid, use the uid from Pattern
            return Pattern.__hash__(self)

    def update(self, other):
        if self.level != other.level:
            raise ValueError("Wrong dixel levels to update!")

        updatable = ["AccessionNumber", "StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID", "PatientID", \
                     "PatientName"]

        for k in updatable:
            v = other.meta.get(k)
            if v:
                # logging.debug("Found an update {}:{}".format(k,v))
                if k.lower().find("date") >= 0:
                    v = dtparser.parse(v)
                self.meta[k] = v

        return self

    @property
    def AccessionNumber(self):
        return self.meta['AccessionNumber']

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

    def get_pixels(self):
        if self.meta['PhotometricInterpretation'] == "RGB":
            pixels = self.pixels.reshape([self.pixels.shape[1], self.pixels.shape[2], 3])
        else:
            pixels = self.pixels

        return pixels
