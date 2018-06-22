# Diana-agnostic Dicom file reading and writing

import logging, os
from typing import Sequence
import attr
import pydicom
import binascii


@attr.s
class DicomFile(object):
    location = attr.ib(default="")

    def fp(self, fn: str, path: str=None, explode: Sequence=None):
        partial = self.location
        if path:
            partial = os.path.join(partial, path)
        if explode:
            epath = self.explode_path(fn, explode[0], explode[1])
            partial = os.path.join(partial, epath)
        fp = os.path.join(partial, fn)
        return fp

    def explode_path(self, fn: str, stride: int, depth: int):
        expath = []
        for i in range(depth):
            block = fn[(i - 1) * stride:i * stride]
            expath.append(block)
        return os.path.join(*expath)

    def write(self, fn: str, data, path: str=None, explode: Sequence=None):
        fp = self.fp(fn, path, explode)

        if not os.path.dirname(fn):
            os.makedirs(os.path.dirname(fn))

        with open(fp, 'wb') as f:
            f.write(data)

    def read(self, fn: str, path: str=None, explode: Sequence=None, pixels: bool=False):
        fp = self.fp(fn, path, explode)

        logging.warning(fp)

        def is_dicom(fp):
            try:
                with open(fp, 'rb') as f:
                    f.seek(0x80)
                    header = f.read(4)
                    magic = binascii.hexlify(header)
                    if magic == b"4449434d":
                        # logging.debug("{} is dcm".format(fp))
                        return True
            except:
                pass

            # logging.debug("{} is NOT dcm".format(fp))
            return False

        if not is_dicom(fp):
            raise Exception("Not a DCM file: {}".format(fp))

        if not pixels:
            dcm = pydicom.read_file(fp, stop_before_pixels=True)
        else:
            dcm = pydicom.read_file(fp)

        return dcm, fp
