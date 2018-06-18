# xArch Orthanc Release Image
# Derek Merck, Spring 2018

ARG RESIN_ARCH="intel-nuc"
#ARG RESIN_ARCH="raspberrypi3"

FROM resin/${RESIN_ARCH}-debian:stretch
MAINTAINER Derek Merck <derek_merck@brown.edu>

# Args for use inside the cross-compiler must be declared inside the cross compiler!
ARG TINI_VERS="v0.18.0"
#ARG TINI_BIN=tini-armhf
ARG TINI_BIN="tini"
ARG DIANA_PW="passw0rd!"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERS}/${TINI_BIN} /bin/tini
RUN chmod +x /bin/tini
ENTRYPOINT ["/bin/tini", "--"]

RUN apt update  \
  && apt install -y \
      git \
      build-essential \
      unzip \
      cmake \
      mercurial \
      uuid-dev \
      libcurl4-openssl-dev \
      liblua5.1-0-dev \
      libgtest-dev \
      libpng-dev \
      libjpeg-dev \
      libsqlite3-dev \
      libssl1.0-dev \
      zlib1g-dev \
      libdcmtk2-dev \
      libboost-all-dev \
      libwrap0-dev \
      libjsoncpp-dev \
      libpugixml-dev

RUN hg clone 'https://bitbucket.org/sjodogne/orthanc' '/opt/orthanc/source' \
    && mkdir '/opt/orthanc/build' \
    && chdir '/opt/orthanc/build' \
    && cmake -DALLOW_DOWNLOADS=ON \
          -DUSE_SYSTEM_MONGOOSE=OFF \
          -DUSE_GOOGLE_TEST_DEBIAN_PACKAGE=ON \
          -DDCMTK_LIBRARIES=dcmjpls \
          -DSTATIC_BUILD=ON \
          -DCMAKE_BUILD_TYPE=Release \
          /opt/orthanc/source \
    && make \
    && make install \
    && mkdir /var/lib/orthanc \
    && mkdir /etc/orthanc

ENV TZ=America/New_York
CMD /usr/local/sbin/Orthanc /etc/orthanc/orthanc.json
EXPOSE 8042 4242
VOLUME /var/lib/orthanc/db/
