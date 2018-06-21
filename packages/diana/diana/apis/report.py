import attr
import re

@attr.s
class RadiologyReport(object):
    text = attr.ib()


@attr.s
class LungScreeningReport(RadiologyReport):

    def current_smoker(self):

        pattern = re.compile( r'(?<! not) (?:a )?(current)(?:ly)? (?!> no[nt])(smok)' )
        match = pattern.findall(self.text)
        return len(match) > 0

    def pack_years(self):

        pattern = re.compile(r"(?P<years>\d{1,4}).*(?=pack).*(?=y(?:ea)?r)")
        match = pattern.findall(self.text)

        if len(match) > 0:
            if max(match) > '0':
                return max(match)

    def years_since_quit(self):

        pattern = re.compile(r"(quit)[^\d]*(\d{1,4}) ?(months|years)?", re.IGNORECASE)
        match = pattern.findall(self.text)

        if len(match) > 0:
            # They quit
            tokens = match[0]
            units = tokens[2]

            if units == "years":
                # print("  Years: {}".format(tokens[1]))
                return tokens[1]
            elif units == "months":
                # print("  Months: {}".format(tokens[1]))
                return int( int(tokens[1])/12 + 1 )
            elif len(tokens[1]) > 3:
                # It's a date
                # print("  Date: {}".format(tokens[1]))
                return 2018-int(tokens[1])

    def lungrads(self):

        pattern = re.compile(r"(?:Lung-RADS)[^\d]*(\d[SC]*)")
        match = pattern.findall(self.text)

        if len(match)>0:
            return match[0]
