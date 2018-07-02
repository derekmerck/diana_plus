"""
diana-star quick-test
Merck, summer 2018

Confirm's basic read/write functionality for local and distributed ("star") api's.
Test different remote control environments by setting broker and service info before
starting any services.

$ pushd test/vagrant && vagrant up && popd
$ ansible-playbook -i test/testbench.yml stack/diana_play.yml
$ celery apps/diana-worker/app.py worker -Q "default,file" -l INFO
$ python3 test/diana_distrib.py

"""

import os

os.environ['DIANA_BROKER']="redis://:D1anA!@rad_research:6379/1"
os.environ['DIANA_RESULT']="redis://:D1anA!@rad_research:6379/2"
service_cfg = "secrets/lifespan_services.yml"

# os.environ['DIANA_BROKER']="redis://:passw0rd!@192.168.33.10:6379/1"
# os.environ['DIANA_RESULT']="redis://:passw0rd!@192.168.33.10:6379/2"
# service_cfg = "test/dev_services.yml"

import logging, yaml, time
from pprint import pprint, pformat
from celery import chain
from diana.apis import Dixel
from diana.utils import DicomLevel
from diana import apis as local_apis
from diana.star import apis as star_apis
from diana.star.tasks import do


def test_local():

    logging.info("**Testing local apis**")

    d = Dixel()
    cache = local_apis.Redis(**services['redis'])
    dfio = local_apis.DicomFile(location="test/resources")
    orthanc = local_apis.Orthanc(**services['orthanc'])

    cache.put(d)
    e = cache.get(d.id)
    assert d == e

    # Polymorphic get for DicomFile
    f = dfio.get("IM66")
    g = dfio.get(f, view="file")
    orthanc.put(g)
    # Polymorphic get for Orthanc
    h = orthanc.get(g.oid(), level=DicomLevel.INSTANCES)
    i = orthanc.get(g)
    assert f.oid() == g.oid() == h.oid() == i.oid()

def test_distrib():

    logging.info("**Testing distributed apis**")

    d = Dixel()
    cache = star_apis.Redis(**services['redis'])
    dfio = star_apis.DicomFile(location="test/resources")
    orthanc = star_apis.Orthanc(**services['orthanc'])

    cache.put(d).get()
    e = cache.get(d.id).get()
    assert d == e

    # Polymorphic get for DicomFile
    f = dfio.get("IM68").get()
    g = dfio.get(f, view="file").get()
    orthanc.put(g).get()
    # Polymorphic get for Orthanc
    h = orthanc.get( g.oid(), level=DicomLevel.INSTANCES ).get()
    i = orthanc.get( g, level=DicomLevel.INSTANCES ).get()
    assert f.oid() == g.oid() == h.oid() == i.oid()

def test_chaining():

    logging.info("**Testing distributed chaining (do) **")

    dfio = star_apis.DicomFile(location="test/resources")
    orthanc = star_apis.Orthanc(**services['orthanc'])

    tasks = chain( do.s(method="get", view="file", pattern=dfio.pattern) |
                   do.s(method="put", pattern=orthanc.pattern) |
                   do.s(method="get", pattern=orthanc.pattern) )

    d = tasks("IM67").get()
    assert d.oid() == "69fc8df0-bde17245-284bcda1-c6506da9-3dd24afb"

    # logging.info("**Testing distributed chaining (oo) **")
    #
    # e = dfio.get.s("IM67")
    #
    # print(e)

    # assert e.oid() == "69fc8df0-bde17245-284bcda1-c6506da9-3dd24afb"

def test_splunk():


    dfio = local_apis.DicomFile(location="test/resources")
    splunk = local_apis.Splunk(**services["splunk"])
    orthanc = local_apis.Orthanc(**services['orthanc'])

    worklist = set()
    for item in ["IM66", "IM67", "IM68"]:
        worklist.add( dfio.get(item, view="file") )

    for item in worklist:
        orthanc.put(item)

    for item in orthanc.instances:
        d = orthanc.get(item)
        splunk.put(d, index="diana", host=orthanc.location, hec="diana")

    result = splunk.find_items("search index=diana")

    time.sleep(5)  # Takes a few secs for Splunk to update it's index

    for item in result:
        print(item.oid())

if __name__=="__main__":

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    with open(service_cfg, "r") as f:
        services = yaml.safe_load(f)

    proxy = local_apis.Orthanc(**services['proxy1'])
    splunk = local_apis.Splunk(**services['splunk'])

    # for item in proxy.instances:
    #     print( item.meta )




    q = {"StudyDate": "20180621",
         "StudyTime": "0800-1000",
         "StudyDescription": '',
         "ModalitiesInStudy": "CT"}

    recent = proxy.find(q, DicomLevel.STUDIES, "gepacs")

    if not recent:
        exit()

    for study in recent:

        desc = "{}: {} at {} ({})".format(study.meta['AccessionNumber'],
                                     study.meta['StudyDescription'],
                                     study.meta['StudyTime'],
                                     study.meta['ModalitiesInStudy'])
        logging.info(desc)

        q = {"StudyInstanceUID": study.meta["StudyInstanceUID"],
             "SeriesDescription": '',
             "Modality": "SR"}
        series = proxy.find(q, DicomLevel.SERIES, "gepacs")

        if not series:
            logging.info("  - NO STRUCTURED REPORT")
            continue

        for s in series:
            desc = "   - {}".format(s.meta['SeriesDescription'])
            logging.info(desc)

            q = {"StudyInstanceUID": study.meta["StudyInstanceUID"],
                 "SeriesInstanceUID": s.meta["SeriesInstanceUID"]}

            ret = proxy.find(q, DicomLevel.SERIES, "gepacs", retrieve=True)
            d = proxy.get(s.oid(), level=DicomLevel.SERIES)
            splunk.put(d, "dose_reports", host=proxy.location, hec="diana")
            proxy.remove(d)

            # instances = proxy.find(q, DicomLevel.INSTANCES, "gepacs")
            # if not instances:
            #     continue
            #
            # instance = instances.pop()
            #
            # logging.warning(instance)
            #
            # q = {"StudyInstanceUID": study.meta["StudyInstanceUID"],
            #      "SeriesInstanceUID": s.meta["SeriesInstanceUID"],
            #      "SOPInstanceUID": instance.meta["SOPInstanceUID"]}
            #
            # proxy.find(q, DicomLevel.INSTANCES, "gepacs", retrieve=True)

            # d = proxy.get( instance.oid(), level=DicomLevel.INSTANCES )
            #
            # print(d)

        # exit()

    # test_local()
    # test_distrib()
    # test_chaining()
    # test_splunk()  # Need an assertion in here


