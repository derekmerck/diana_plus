ARG RESIN_ARCH="intel-nuc"
#ARG RESIN_ARCH="raspberrypi3"

FROM resin/${RESIN_ARCH}-debian:stretch
MAINTAINER Derek Merck <derek_merck@brown.edu>

ARG DIANA_PW="passw0rd!"

RUN apt-get update \
    && apt-get install -yq --no-install-recommends \
         openssh-server \
    && apt-get clean

# Set up the config for openSSH.  Stretch has PermitRootLogin commented by default
RUN mkdir /var/run/sshd \
    && echo "root:${DIANA_PW}" | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

EXPOSE 22

ENV TZ=America/New_York
# Enable resin.io's systemd init system
ENV INITSYSTEM off

#CMD service ssh start  # requires "privilidged"
CMD /usr/sbin/sshd -D