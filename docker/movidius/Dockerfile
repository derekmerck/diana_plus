# xArch Movidius Machine Learning (Caffe) Image
# Derek Merck, Spring 2018

# Cribbed in part from:
# - https://github.com/movidius/ncsdk/tree/ncsdk2/extras/docker

ARG RESIN_ARCH="intel-nuc"

FROM resin/${RESIN_ARCH}-debian:stretch
MAINTAINER Derek Merck <derek_merck@brown.edu>

RUN apt update \
    && apt install -y --no-install-recommends \
         git \
         sed \
         build-essential \
         sudo \
         tar \
         udev \
         wget \
         python3-dev \
         python3-numpy-dev \
         python3-setuptools \
         python3-pip \
         python \
         python-pip \
         python-setuptools \
         software-properties-common \
         libfreetype6-dev \
         libpng-dev \
         pkg-config \
    && apt-get clean

RUN git clone -b ncsdk2 https://github.com/movidius/ncsdk /ncsdk2 \
    && sed -i 's/exit 1//g' /ncsdk2/install.sh

WORKDIR /ncsdk2
RUN make install

ENV TZ=America/New_York
# Enable resin.io's systemd init system
ENV INITSYSTEM on

CMD tail -f /dev/null