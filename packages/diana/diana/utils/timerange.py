import re
from datetime import datetime, timedelta
import attr
from dateutil import parser as timeparser
from .dicom import dicom_strftime


@attr.s
class TimeRange(object):
    start = attr.ib()
    end = attr.ib()

    def __attrs_post_init__(self):

        if type(self.start) == datetime or \
            type(self.start) == timedelta:
            _start = self.start
        else:
            _start = TimeRange.convert(self.start)

        if type(self.end) == datetime or \
            type(self.end) == timedelta:
            _end = self.end
        else:
            _end = TimeRange.convert(self.end)

        if type(_start) == datetime:
            self.start = _start
        elif type(_end) == datetime:
            self.start = _end + _start
        else:
            self.start = datetime.now() + _start

        if type(_end) == datetime:
            self.end = _end
        elif type(_start) == datetime:
            self.end = _start + _end
        else:
            self.end = datetime.now() + _end

    @classmethod
    def convert(cls, time_str: str) -> timedelta:

        # Check for 'now'
        if time_str == "now":
            return datetime.now()

        # Check for a delta
        delta_re = re.compile("([+-]?)(\d*)([y|m|w|d|h|m|s])")
        match = delta_re.match(time_str)

        if match:

            dir = match.groups()[0]
            val = match.groups()[1]
            unit = match.groups()[2]

            if unit == "s":
                seconds = int(val)
            elif unit == "m":
                seconds = int(val) * 60
            elif unit == "h":
                seconds = int(val) * 60 * 60
            elif unit == "d":
                seconds = int(val) * 60 * 60 * 24
            elif unit == "w":
                seconds = int(val) * 60 * 60 * 24 * 7
            elif unit == "m":
                seconds = int(val) * 60 * 60 * 24 * 30
            elif unit == "y":
                seconds = int(val) * 60 * 60 * 24 * 365
            else:
                raise ValueError

            if dir == "-":
                seconds = seconds * -1

            return timedelta(seconds=seconds)

        # Check for a parsable time - this handles DICOM format fine
        time = timeparser.parse(time_str)
        if type(time) == datetime:
            return time

        raise ValueError("Can not parse time: {}".format(time_str))

    def as_dicom(self):
        return dicom_strftime(self.start), dicom_strftime(self.end)

    def __str__(self):
        str = "({}, {})".format(self.start, self.end)
        return str

def test_time_formatter():

    TR = TimeRange( "now", "+4h" )
    print(TR)

    TR = TimeRange( "June 2, 2017", "June 14, 2019" )
    print(TR)

    TR = TimeRange( "+3h", "-3h" )
    print(TR)

    print( TR.as_dicom() )

    TR = TimeRange("20180603120000", "+3h")
    print(TR)


if __name__ == "__main__":

    test_time_formatter()
