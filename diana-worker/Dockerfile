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

ARG DIANA_PW="passw0rd!"

# If aarch64, there is no security repo for jessie (but there is for stretch)
# RUN sed -i 's$deb http://security.debian.org/debian-security jessie/updates main$$g' /etc/apt/sources.list

RUN apt update  \
    && apt install -y --no-install-recommends git \
    && apt-get clean \
    && useradd -ms /bin/bash diana && echo "diana:${DIANA_PW}" | chpasswd \
    && git clone https://github.com/derekmerck/diana_plus /home/diana/source \
    && chown -R diana /home/diana/source \
    && pip3 install -e /home/diana/source/packages/diana

ENV TZ=America/New_York
# Enable resin.io's systemd init system
ENV INITSYSTEM on

USER diana
WORKDIR /home/diana/source/apps
CMD python3 diana-star/app.py worker