Diana+
===================

[Merck][], Summer 2018

[Merck]: derek_merck@brown.edu


Organization
------------------

### diana package

- `utils` contains generic code with no references to diana-dixels or endpoints.
- `apis` contains get/put/handle functions for diana-dixels and endpoints
- `daemon` contains higher level tasks that compose multiple apis, like file monitoring for example
- `star` overloads apis with a celery-friendly wrapper function (something like 
  `do-star(object, func, item)`)
  
Can also be installed with `pip3 install diana_plus`
  
### guidmint package

- implements "mints" for generating repeatable global uids and sham names/dobs


### apps

- [cli](apps/cli) contains command-line interface wrappers for common diana functions such as querying endpoints and saving images
- [diana-worker](apps/diana-worker) creates a diana+ celery worker ("diana*")
- [get-a-guid](apps/get-a-guid) is a REST API for `guidmint`
- [radcatr](apps/radcatr) is a simple TKL UI for basic report review and annotation
- `study-manager` is a web portal for organizing access to multiple study archives
  
  
### stack


  
### docker

- [docker](docker) includes `docker-compose` configurations and container descriptions (Dockerfiles) for building `diana-worker` and the release version of `orthanc` for Debian.  These containers are built for both `amd64` and `arm32v7` architectures on travis as part of testing, so they are always available from docker hub at `derekmerck/diana-worker` and `derekmerck/orthanc` respectively. 
  
  
### tests

- [resources](tests/resources) includes some simple, anonymized DICOM files are included to test apis for upload, download,
caching, etc.
- [bench](tests/bench) provides a dev configuraqtion for testing with vagrant
- [unit](tests/unit) collection of short function verfications

See <test/README.md>




Service Stack
-------------------

A simple Diana+ stack requires 2 basic services:

- An Orthanc DICOM node for storing, pulling, proxying DICOM data
- A Splunk database for indexing available data

Additional services can be added:

- File handlers for reading/writing DCM, png, text, and csv files
- Persistent (Redis, csv) or in-memory caches for worklist
- Report handlers for extracting and anonymizing report data

A set of distributed "star" apis shadow the vanilla class names for building workflows with the celery async manager.  In this case, two additional services are required:

- A Redis messenger
- One or more "diana-workers" attached to various queues depending on their hardware (file or report access, machine learning hardware, proxying ip)

A basic stack can be configured with Ansible using vagrant and the `testbench.yml` inventory.  
The `diana_play.yml` playbook is also used with a private inventory to setup the Lifespan CIRR.
