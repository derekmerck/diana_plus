# Diana-agnostic Dicom file reading and writing

import logging, os
import attr
import pydicom
import binascii


@attr.s
class DicomFile(object):
    location = attr.ib(default="")

    def fp(self, fn, path=None, explode=None):
        partial = self.location
        if path:
            partial = os.path.join(partial, path)
        if explode:
            epath = self.explode_path(fn, explode[0], explode[1])
            partial = os.path.join(partial, epath)
        fp = os.path.join(partial, fn)
        return fp

    def explode_path(self, fn, stride, depth):
        expath = []
        for i in range(depth):
            block = fn[(i - 1) * stride:i * stride]
            expath.append(block)
        return os.path.join(*expath)

    def write(self, fn, data, path=None, explode=None):
        fp = self.fp(fn, path, explode)

        if not os.path.dirname(fn):
            os.makedirs(os.path.dirname(fn))

        with open(fp, 'wb') as f:
            f.write(data)

    def read(self, fn, path=None, explode=None, pixels=False):
        fp = self.fp(fn, path, explode)

        def is_dicom(fp):
            with open(fp, 'rb') as f:
                f.seek(0x80)
                header = f.read(4)
                magic = binascii.hexlify(header)
                if magic == b"4449434d":
                    # logging.debug("{} is dcm".format(fp))
                    return True
            # logging.debug("{} is NOT dcm".format(fp))
            return False

        if not is_dicom(fp):
            raise Exception("Not a DCM file: {}".format(fp))

        if not pixels:
            dcm = pydicom.read_file(fp, stop_before_pixels=True)
        else:
            dcm = pydicom.read_file(fp)

        return dcm, fp
