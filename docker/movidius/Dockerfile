# Cribbed in part from:
# - https://github.com/movidius/ncsdk/tree/ncsdk2/extras/docker

#ARG ARCH_TAG="amd64"
#FROM derekmerck/learn:$ARCH_TAG

ARG RESIN_ARCH="intel-nuc"

FROM resin/${RESIN_ARCH}-debian:stretch
MAINTAINER Derek Merck <derek_merck@brown.edu>

# Args for use inside the cross-compiler must be declared inside the cross compiler!
ARG TINI_VERS="v0.18.0"
ARG TINI_BIN="tini"
ARG DIANA_PW="passw0rd!"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERS}/${TINI_BIN} /bin/tini
RUN chmod +x /bin/tini
ENTRYPOINT ["/bin/tini", "--"]

# Install necessary packages for the installer
RUN apt-get update && apt-get install -y \
    build-essential \
    sed \
    sudo \
    tar \
    udev \
    wget \
    && apt-get clean


RUN apt install -y --no-install-recommends \
         sed \
         build-essential \
         sudo \
         tar \
         udev \
         wget \
    && apt-get clean

#         python3-numpy-dev \
#    && pip3 install -U pip \
    # && pip2 install -U pip \
RUN git clone -b ncsdk2 https://github.com/movidius/ncsdk /ncsdk2 \
    && sed -i 's/exit 1//g' /ncsdk2/install.sh

WORKDIR /ncsdk2
RUN make install

ENV TZ=America/New_York
CMD tail -f /dev/null