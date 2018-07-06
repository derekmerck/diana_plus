# Diana-agnostic DICOM info

import logging
from enum import Enum
from hashlib import sha1
from datetime import datetime

logger = logging.getLogger(__name__)


class DicomLevel(Enum):
    PATIENTS  = 0
    STUDIES   = 1
    SERIES    = 2
    INSTANCES = 3

    # Provides a partial ordering so they are comparable
    # Note that Study < Instance under this order
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            # logging.debug("{}<{}".format(self.value, other.value))
            return self.value < other.value
        return NotImplemented

    @classmethod
    def of(cls, value: str):
        if value.lower()=="instances":
            return DicomLevel.INSTANCES
        elif value.lower()=="series":
            return DicomLevel.SERIES
        elif value.lower()=="studies":
            return DicomLevel.STUDIES

        return DicomLevel.PATIENTS

    def parent_level(self):
        if self == DicomLevel.PATIENTS:
            raise ValueError
        return DicomLevel( int(self) + 1 )

    def child_level(self):
        if self == DicomLevel.INSTANCES:
            raise ValueError
        return DicomLevel( int(self) - 1 )

    def __str__(self):
        return '{0}'.format(self.name.lower())


def orthanc_id(PatientID, StudyInstanceUID, SeriesInstanceUID=None, SOPInstanceUID=None) -> str:
    if not SeriesInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID])
    elif not SOPInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID])
    else:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID])
    h = sha1(s.encode("UTF8"))
    d = h.hexdigest()
    return '-'.join(d[i:i+8] for i in range(0, len(d), 8))


def dicom_strptime( dts: str ) -> datetime:

    if not dts:
        logger.error("Failed to parse empty date time string")
        ts = datetime.now()
        return ts

    try:
        # GE Scanner dt format
        ts = datetime.strptime( dts , "%Y%m%d%H%M%S")
        return ts
    except ValueError:
        # Wrong format
        pass

    try:
        # Siemens scanners use a slightly different aggregated format with fractional seconds
        ts = datetime.strptime( dts , "%Y%m%d%H%M%S.%f")
        return ts
    except ValueError:
        # Wrong format
        pass

    logger.error("Failed to parse date time string: {0}".format( dts ))
    ts = datetime.now()
    return ts


def dicom_strftime( dt: datetime ) -> str:
    return dt.strftime( "%Y%m%d%H%M%S" )


def dicom_strfdate( dt: datetime ) -> str:
    return dt.strftime( "%Y%m%d" )


def dicom_strftime2( dt: datetime ) -> (str, str):
    return (dt.strftime( "%Y%m%d" ), dt.strftime( "%H%M%S" ))
