# xArch Machine Learning (Keras+TF) Image
# Derek Merck, Spring 2018

# Cribbed in part from
# - https://github.com/DeftWork/tensorflow-py3
# - https://github.com/gw0/docker-keras

ARG RESIN_ARCH="intel-nuc"

FROM resin/${RESIN_ARCH}-python:3
MAINTAINER Derek Merck <derek_merck@brown.edu>

# Args for use inside the cross-compiler must be declared inside the cross compiler!
ARG TINI_VERS="v0.18.0"
ARG TINI_BIN="tini"
ARG DIANA_PW="passw0rd!"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERS}/${TINI_BIN} /bin/tini
RUN chmod +x /bin/tini
ENTRYPOINT ["/bin/tini", "--"]

RUN apt update \
    && apt install -y --no-install-recommends \
         git \
         build-essential \
         unzip \
         curl \
         rsync \
         software-properties-common \
         libfreetype6-dev \
         libpng12-dev \
         libzmq3-dev \
         pkg-config \
    && apt-get clean

#         python3 \
#         python3-dev \
#         python3-pip \
#         python3-setuptools \
#         python3-wheel \

         # requirements for numpy
#         libopenblas-base \
#         python3-numpy \
#         python3-scipy \

         # requirements for keras
#         python3-h5py \
#         python3-yaml \
#         python3-pydot

# Official amd64
ARG TF_WHL_URL=https://storage.googleapis.com/tensorflow/linux/cpu/
ARG TF_WHL_FILE=tensorflow-1.9.0rc0-cp34-cp34m-linux_x86_64.whl

# Official arm32v7
#  -  http://ci.tensorflow.org/view/Nightly/job/nightly-pi-python3/lastSuccessfulBuild/artifact/output-artifacts/tensorflow-1.9.0rc0-cp34-none-linux_armv7l.whl
# Older and doesn't install clean
#  - https://github.com/samjabrahams/tensorflow-on-raspberry-pi/releases/download/v1.1.0/tensorflow-1.1.0-cp27-none-linux_armv7l.whl

RUN pip3 --no-cache-dir install --upgrade pip setuptools
# Stuff for notebook + ml
#         ipykernel \
#         jupyterlab \
#         matplotlib \
#         numpy \
#         sklearn \
#         pandas \
RUN curl -O ${TF_WHL_URL}${TF_WHL_FILE} \
    && mv ${TF_WHL_FILE} tensorflow-1.9.0rc0-py3-none-any.whl \
    && pip3 --no-cache-dir install tensorflow-1.9.0rc0-py3-none-any.whl \
    && rm -f tensorflow-1.9.0rc0-py3-none-any.whl \
#    && python3 -m ipykernel.kernelspec

# Suppress TF log warnings
ENV TF_CPP_MIN_LOG_LEVEL=2

ENV KERAS_BACKEND=tensorflow
RUN pip3 --no-cache-dir install keras

# quick test and dump package lists
RUN python3 -c "import tensorflow; print(tensorflow.__version__)" \
 && dpkg-query -l > /dpkg-query-l.txt \
 && pip3 freeze > /pip3-freeze.txt

#COPY jupyter_notebook_config.py /root/.jupyter/
#
## Copy sample notebooks.
#COPY notebooks /notebooks

#EXPOSE 8888

#WORKDIR "/notebooks"

#CMD jupyter lab --ip=* --no-browser --allow-root

ENV TZ=America/New_York
CMD tail -f /dev/null
