"""
In principle, there ought to be a number of different porters

proxy -> files  (w/wo anon)
proxy -> splunk (w/wo anon)

orthanc -> files
orhtanc -> splunk

files -> orthanc
files -> splunk

"""

import logging
import attr
from diana.apis import MetaCache, Orthanc, DicomFile

@attr.s
class Porter(object):
    source = attr.ib( type=Orthanc )
    proxy_domain = attr.ib( type=str )
    dest = attr.ib( type=DicomFile )
    explode = attr.ib( default=None )
    # anonymize = attr.ib( default=True )

    def run(self, dixels: MetaCache):

        for d in dixels:

            # Check for unfindable
            if not d.meta.get("StudyInstanceUID"):
                logging.debug("Skipping {} - apparently unfindable".format(d.meta["ShamAccession"]))
                continue

            # Check and see if file already exists
            if self.dest.check(d, fn_from="ShamAccession", explode=self.explode):
                logging.debug("Skipping {} - already exists".format(d.meta["ShamAccession"]))
                continue

            # Shouldn't have a self-mutating function that can go to None...
            my_accession = d.meta['ShamAccession']
            d = self.source.find_item(d, self.proxy_domain, True)

            if not d:
                # obviously not d b/c d is None by now...
                logging.debug("Skipping {} - found but unretrievable".format(my_accession))
                continue

            try:
                e = self.source.anonymize(d)
            except:
                logging.debug("Skipping {} - can not anonymize (bad uid?)".format(d.meta["ShamAccession"]))
                continue

            e = self.source.get(e, view="archive")

            self.dest.put(e, fn_from="AccessionNumber", explode=self.explode)

            # Clean up proxy as you go
            self.source.remove(d)
            self.source.remove(e)





