# xArch Machine Learning (Keras+TF) Image
# Derek Merck, Spring 2018

# Cribbed in part from
# - https://github.com/DeftWork/tensorflow-py3
# - https://github.com/gw0/docker-keras

ARG RESIN_ARCH="intel-nuc"

FROM resin/${RESIN_ARCH}-python:3.4
MAINTAINER Derek Merck <derek_merck@brown.edu>

# Official amd64
ARG TF_WHL_URL=https://storage.googleapis.com/tensorflow/linux/cpu/
ARG TF_WHL_FILE=tensorflow-1.9.0rc0-cp34-cp34m-linux_x86_64.whl

# Official arm32v7
#ARG TF_WHL_URL=http://ci.tensorflow.org/view/Nightly/job/nightly-pi-python3/lastSuccessfulBuild/artifact/output-artifacts/
#ARG TF_WHL_FILE=tensorflow-1.9.0rc0-cp34-none-linux_armv7l.whl

RUN apt update  \
    && apt install -y --no-install-recommends \
         libopenblas-base \
         libhdf5-dev \
         libatlas-base-dev \
         libatlas-dev

RUN pip3 --no-cache-dir install \
         pyyaml \
         numpy \
         h5py \
         scipy \
         pydot

RUN curl -O ${TF_WHL_URL}${TF_WHL_FILE} \
    && pip3 install ${TF_WHL_FILE}

ENV KERAS_BACKEND=tensorflow

RUN pip3 install keras \
    && rm -f ${TF_WHL_FILE}

ENV TZ=America/New_York
# Enable resin.io's systemd init system
ENV INITSYSTEM on

CMD tail -f /dev/null
