# Embedded-diana


## Supported architectures

`amd64` -- desktop computers/vms, UP boards
`arm32v7` -- raspberry pi 3, Beagleboard
`arm64v8` -- NVIDIA Jetson TX2


## Building service containers

`docker-builder.yml` contains build descriptions for all services and relevant architectures.

`$ docker-compose -f docker-builder.yml build diana-worker, orthanc`

* diana-worker (amd64, arm32v7, arm64v8)
* orthanc (amd64, arm32v7, arm64v8)
* tf-keras (cpu only, amd64, arm32v7)
* movidius (amd64, arm32v7)


Resin.io base images are used, so they can be cross-compiled on any system.
Travis will easily compile the `amd64` images, but the other ones take too long.
Packet's ARMv8 server instances can be used to compile `arm64v8` containers.
No good solution for `arm32v7` yet other than tedious local builds.


## arm64v8 builds on Packet

```
$ apt update
$ apt upgrade
$ curl -fsSL get.docker.com -o get-docker.sh
$ sh get-docker.sh 
$ docker run hello-world
$ apt install git python-pip
$ pip install docker-compose
$ git clone http://github.com/derekmerck/diana_plus
$ cd diana_plus/docker
$ docker-compose -f docker-compose.build.yml build orthanc-arm64v8 , etc...
```


## Multiarch

After building new images, call `manifest-it.py` to push updated images and build the Docker
multiarchitecture service mappings.

```bash
$ python3 manifest-it rcd-manifests.yml
```