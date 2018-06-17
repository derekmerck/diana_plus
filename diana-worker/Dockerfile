# Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'diana_services.yml' is copied or mounted to /etc/diana_services.yml
# - Change the queue by overriding CMD on start up
#   e.g., command="python3 diana-star/app.py worker -B -Q my_queue"

FROM python:3.6-stretch
MAINTAINER Derek Merck <derek_merck@brown.edu>

ARG TINI_VERSION=v0.18.0
ARG TINI_BINARY=tini
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/${TINI_BINARY} /bin/tini
RUN chmod +x /bin/tini
ENTRYPOINT ["/bin/tini", "--"]

RUN apt update  \
    && apt install -y git \
    && useradd -ms /bin/bash diana && echo "diana:passw0rd!" | chpasswd \
    && git clone https://github.com/derekmerck/diana_plus /home/diana/source \
    && chown -R diana /home/diana/source \
    && pip install -e /home/diana/source/packages/diana

ENV TZ=America/New_York
USER diana
WORKDIR /home/diana/source/apps
CMD python3 diana-star/app.py worker