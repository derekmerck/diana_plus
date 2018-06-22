"""
Hashes an alphanumeric guid from a given string value

* Given a guid, gender (M/F/U), and name lists -> returns a reproducible pseudonym
* Given a guid, and dob (%Y-%m-%d) -> returns a reproducible pseudodob within 6 months of the original dob
* Given a guid, and age (delta Y) -> pseudodob of guid, (now - age*365.25 days); it is NOT reproducible b/c it depends on now


pseudonym for id

pseudodob for id, dob OR age + studydate

id from key

key from name, gender=U, dob OR age + studydate
key from mrn
key from


"""

import logging

import random
from dateutil import parser as dateparser
from datetime import datetime, timedelta
import os
from abc import abstractmethod

__version__ = "0.11.0"

DEFAULT_MAX_DATE_OFFSET = int(365/2)   # generated pseudodob is within 6 months
DEFAULT_HASH_PREFIX_LENGTH = 16  # 8 = 64bits, -1 = entire value

class GUIDMint(object):
    """
    Abstract= base class for guid mints.
    """

    def __init__(self,
                 max_date_offset = DEFAULT_MAX_DATE_OFFSET,
                 hash_prefix_length = DEFAULT_HASH_PREFIX_LENGTH,
                 **kwargs):
        self.__version__ = __version__
        self.max_date_offset = max_date_offset
        self.hash_prefix_length = hash_prefix_length
        self.logger = logging.getLogger(self.name())

    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def guid(self, value: str, *args, **kwargs):
        raise NotImplementedError

    def pseudodob(self, guid, dob=None, age=None, ref_date=None, *args, **kwargs) -> datetime:
        random.seed(guid)

        if not dob:
            if not age:
                age = random.randint(19,65)

            age = int(age)

            if not ref_date:
                logging.warning("Generating unrepeatable pseudodob using 'now' as the age reference date")
                ref_date = datetime.now()
            elif type(ref_date) != datetime:
                ref_date = dateparser.parse(ref_date)

            dob = ref_date-timedelta(days=age*365.25)

        elif not isinstance(dob, datetime):
            dob = dateparser.parse(dob)

        r = random.randint(-self.max_date_offset, self.max_date_offset)
        rd = timedelta(days=r)

        return (dob+rd).date()



def test_mints():

    md5_mint = MD5Mint()
    pseudo_mint = PseudoMint()

    name = "MERCK^DEREK^L"
    gender = "M"
    dob = "1971-06-06"

    id = md5_mint.pseudo_identity(name, gender=gender, dob=dob)
    assert(id==('392ec5209964bfad', '392ec5209964bfad', '1971-08-23'))
    id = pseudo_mint.pseudo_identity(name, gender=gender, dob=dob)
    assert(id==(u'BIN4K4VMOBPAWTW5', u'BERTOZZI^ISIDRO^N', '1971-06-22'))

    name = "MERCK^LISA^H"
    gender = "F"
    dob = "1973-01-01"

    id = md5_mint.pseudo_identity(name, gender=gender, dob=dob)
    assert(id==('2951550cc186aae1', '2951550cc186aae1', '1972-09-03'))
    id = pseudo_mint.pseudo_identity(name, gender=gender, dob=dob)
    assert(id==(u'LSEOMWPHUXQTPSN3', u'LIZARDO^SUMMER^E', '1972-10-22'))

    name = "PROTECT3-SU001"
    age = 65

    id = md5_mint.pseudo_identity(name, age=age)
    assert(id==('c3352e0d6de56475', 'c3352e0d6de56475', '1966-09-24'))
    id = pseudo_mint.pseudo_identity(name, age=age)
    assert(id==(u'KGHZ7YTCPDDAXG2N', u'KUNZMAN^GENIE^H', '1952-11-11'))


