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

# os.environ['DIANA_BROKER']="redis://:D1anA!@rad_research:6379/1"
# os.environ['DIANA_RESULT']="redis://:D1anA!@rad_research:6379/2"
# service_cfg = "secrets/lifespan_services.yml"

os.environ['DIANA_BROKER']="redis://:passw0rd!@192.168.33.10:6379/1"
os.environ['DIANA_RESULT']="redis://:passw0rd!@192.168.33.10:6379/2"
service_cfg = "test/dev_services.yml"

import logging, yaml
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

    logging.info("**Testing distributed chaining (oo) **")

    e = dfio.get.s("IM67")

    print(e)

    # assert e.oid() == "69fc8df0-bde17245-284bcda1-c6506da9-3dd24afb"

if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)

    with open(service_cfg, "r") as f:
        services = yaml.safe_load(f)

    test_local()
    test_distrib()
    test_chaining()
