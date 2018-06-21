# Requires workers with "default", "learn", and "file" queues

import logging
import os, yaml
from celery import chain
from diana.apis import Dixel
from diana.utils import DicomLevel
from diana.star.apis import Redis, DicomFile, Orthanc


def test_batching(count=20):
    project = "test"
    worklists = Redis().inventory

    worklists.delete( project )
    for i in range(count):
        item = Dixel()
        redis.put(item)
        worklists.sadd(project, item.id)

    worklist = worklists.smembers( project )
    print(worklist)

    # Dispatch them all for handling
    for item_id in worklist:
        item = redis.starget(item_id)
        item = clf.starhandle(item)
        assert (item.meta.get('classified'))


def test_celery():

    dx = files.get("IM2", file=True).get()
    dx_oid = dx.oid()

    orthanc.put(dx)
    ex = orthanc.get(dx_oid, DicomLevel.INSTANCES).get()
    assert ex.oid() == dx_oid

    fx = clf.classify(ex).get()
    assert fx.meta.get('classified') == True

    redis.put(fx).get()  # Have to block before getting
    gx = redis.get(fx.id).get()
    assert fx == gx

    hx = files.get("IM3", file=True).get()
    orthanc.put(hx).get()

    s0 = chain( orthanc.get_s(dx.oid(), DicomLevel.INSTANCES) | clf.classify_s() | redis.put_s() )()
    s1 = chain( orthanc.get_s(hx.oid(), DicomLevel.INSTANCES) | clf.classify_s() | redis.put_s() )()

    s0.get()
    s1.get()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    logging.debug("Simple Distributed Diana Test Script")

    service_cfg = os.environ.get("DIANA_SERVICES_CFG", "./services.yml")
    with open(service_cfg, "r") as f:
        services = yaml.safe_load(f)

    dcm_dir = "tests/resources"
    dcm_files = DicomFile(location=dcm_dir)

    orthanc = Orthanc(**services['orthanc'])
    redis = Redis(**services['redis'])

    test_celery()
