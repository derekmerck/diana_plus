# Diana-agnostic DICOM info

import logging
from enum import Enum
from hashlib import sha1
from datetime import datetime

class DicomLevel(Enum):
    PATIENTS  = 0
    STUDIES   = 1
    SERIES    = 2
    INSTANCES = 3

    def parent_level(self):
        if self == DicomLevel.PATIENTS:
            raise ValueError
        return self + 1

    def child_level(self):
        if self == DicomLevel.INSTANCES:
            raise ValueError
        return self - 1

    def __str__(self):
        return '{0}'.format(self.name.lower())


def orthanc_id(PatientID, StudyInstanceUID, SeriesInstanceUID=None, SOPInstanceUID=None):
    if not SeriesInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID])
    elif not SOPInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID])
    else:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID])
    h = sha1(s.encode("UTF8"))
    d = h.hexdigest()
    return '-'.join(d[i:i+8] for i in range(0, len(d), 8))


def dicom_strftime( dtm ):

    try:
        # GE Scanner dt format
        ts = datetime.strptime( dtm , "%Y%m%d%H%M%S")
        return ts
    except ValueError:
        # Wrong format
        pass

    try:
        # Siemens scanners use a slightly different aggregated format with fractional seconds
        ts = datetime.strptime( dtm , "%Y%m%d%H%M%S.%f")
        return ts
    except ValueError:
        # Wrong format
        pass

    logging.error("Can't parse date time string: {0}".format( dtm ))
    ts = datetime.now()
    return ts


def dicom_strptime( dts ):
    return datetime.strptime( dts, "%Y%m%d%H%M%S" )
