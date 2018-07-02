"""
Derek Merck, Summer 2018

Method to summarize collections of Osimis-style ROI metadata and
monkey-patch for diana.apis.Orthanc

Should probably implement this as a subclass of Orthanc that extends "get" with
"view=annotation".  But patching seemed easier for one-off applications.

>>> from diana.apis import Orthanc, osimis_extras
>>> o = Orthanc()
>>> a = o.get_annotations(my_study)

"""

import logging, json, pprint
from typing import Union
from . import Orthanc, Dixel
from ..utils import DicomLevel


def get_annotation(source: Orthanc, study: Dixel) -> Union[dict, None]:

    try:
        resource = "studies/{}/attachments/9999/data".format(study.oid())
        ret = source.gateway.get(resource)
        ret = json.loads(ret)

    except:
        logging.warning("No annotations to retrieve")
        return

    study_annotations = {
        'AccessionNumber': study.meta["AccessionNumber"],
        'StudyInstanceUID': study.meta["StudyInstanceUID"],
        'Annotations': []
    }

    # logging.debug( pprint.pformat(ret) )

    for k, v in ret.items():
        if not v:
            # Sometimes just an empty dict
            continue

        oid = k.split(":")[0]  # format is oid:0, presumably to support multiple users

        instance = source.get(oid, level=DicomLevel.INSTANCES)

        # logging.debug( pprint.pformat(instance.meta) )

        for data in ret[k]['ellipticalRoi']['data']:
            annotation = {
                'ImagePositionPatient': instance.meta['ImagePositionPatient'],
                'SOPInstanceUID': instance.meta['SOPInstanceUID'],
                'SeriesInstanceUID': instance.meta['SeriesInstanceUID'],
                "ROIStart": (
                    data['handles']['start']['x'],
                    data['handles']['start']['y']
                ),
                "ROIEnd": (
                    data['handles']['end']['x'],
                    data['handles']['end']['y']
                ),
                "ROIImageSize": (
                    data['imageResolution']['width'],
                    data['imageResolution']['height']
                )
            }

            # logging.debug( pprint.pformat(ret[k]['ellipticalRoi']) )
            study_annotations['Annotations'].append(annotation)

    # logging.debug( pprint.pformat(study_annotations) )
    return study_annotations


# Monkey-patch
Orthanc.get_annotation = get_annotation

