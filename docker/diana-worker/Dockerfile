# xArch Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'diana_services.yml' is copied or mounted to /etc/diana/services.yml
# - Change the queue by overriding CMD on start up
#   e.g., command="python3 diana-star/app.py worker -B -Q my_queue"

ARG RESIN_ARCH="intel-nuc"
#ARG RESIN_ARCH="raspberrypi3"

FROM resin/${RESIN_ARCH}-python:3
MAINTAINER Derek Merck <derek_merck@brown.edu>

ARG TINI_VERS="v0.18.0"
ARG TINI_BIN="tini"
#ARG TINI_BIN=tini-armhf
ARG DIANA_PW="passw0rd!"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERS}/${TINI_BIN} /bin/tini
RUN chmod +x /bin/tini
ENTRYPOINT ["/bin/tini", "--"]

RUN apt update  \
    && apt install -y --no-install-recommends git \
    && useradd -ms /bin/bash diana && echo "diana:${DIANA_PW}" | chpasswd \
    && git clone https://github.com/derekmerck/diana_plus /home/diana/source \
    && chown -R diana /home/diana/source \
    && pip install -e /home/diana/source/packages/diana

ENV TZ=America/New_York
USER diana
WORKDIR /home/diana/source/apps
CMD python3 diana-star/app.py worker