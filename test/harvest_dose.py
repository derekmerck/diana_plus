import logging, yaml
from diana.apis import Orthanc, Splunk
from diana.daemon import HarvestCTSR

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    service_cfg = "secrets/lifespan_services.yml"

    with open(service_cfg, "r") as f:
        services = yaml.safe_load(f)

    proxy = Orthanc(**services['proxy1'])
    splunk = Splunk(**services['splunk'])

    H = HarvestCTSR(source=proxy, source_domain="gepacs",
                  dest=splunk, dest_domain="dose_reports", dest_hec="diana",
                  start="now", incr="-15m",
                  repeat_until=True)

    H.run()