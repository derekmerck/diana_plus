import os

# os.environ['DIANA_BROKER']="redis://:D1anA!@rad_research:6379/1"
# os.environ['DIANA_RESULT']="redis://:D1anA!@rad_research:6379/2"
# service_cfg = "secrets/lifespan_services.yml"

os.environ['DIANA_BROKER']="redis://:passw0rd!@192.168.33.10:6379/1"
os.environ['DIANA_RESULT']="redis://:passw0rd!@192.168.33.10:6379/2"
service_cfg = "test/dev_services.yml"

import logging, yaml
from diana.apis import Dixel
from diana.utils import DicomLevel
from diana import apis as local_apis
from diana.star import apis as star_apis


"""
Workflow:

- Load file from disk
- Put it into orthanc1 and get oid
- Send it to orthanc2
- Download meta from orthanc2
- Compare meta to original file

"""

def test_local():

    logging.info("Testing local apis")

    d = Dixel()
    cache = local_apis.Redis(**services['redis'])

    cache.put(d)
    e = cache.get(d.id)

    assert d == e

    dfio = local_apis.DicomFile(location="test/resources")
    orthanc = local_apis.Orthanc(**services['orthanc'])

    f = dfio.get("IM66", file=True)
    orthanc.put(f)

    g = orthanc.get(f.oid(), level=DicomLevel.INSTANCES)

    assert f.oid() == g.oid()

def test_distrib():

    logging.info("Testing distributed apis")

    d = Dixel()
    d_id = d.id
    cache = star_apis.Redis(**services['redis'])

    cache.put(d).get()
    e = cache.get(d_id).get()

    assert d == e

    dfio = star_apis.DicomFile(location="test/resources")
    orthanc = star_apis.Orthanc(**services['orthanc'])

    f = dfio.get("IM66", file=True).get()
    orthanc.put(f).get()
    g = orthanc.get( f.oid(), level=DicomLevel.INSTANCES ).get()

    assert f.oid() == g.oid()


if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)

    with open(service_cfg, "r") as f:
        services = yaml.safe_load(f)

    test_local()

    test_distrib()


