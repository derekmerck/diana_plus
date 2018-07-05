Diana-Star
===================

Merck, Summer 2018


Service Stack
-------------------

A Diana-stack uses 2 basic services:

- An Orthanc DICOM node for storing, pulling, proxying DICOM data
- A Splunk database for indexing available data

Additional services can be added:

- FileHandlers for reading/writing DCM, png, text, and csv files
- Persistent (Redis, csv) or in-memory caches for worklist
- ReportHandlers for extracting and anonymizing report data

A set of distributed "star" apis shadow the vanilla class names for building workflows with the celery async manager.  In this case, two additional services are required:

- A Redis messenger
- One or more "diana-workers" attached to various queues depending on their hardware (file access, machine learning hardware, proxying ip)

A basic stack can be configured with Ansible using vagrant and the `testbench.yml` inventory.  
The `diana_play.yml` playbook is also used with a private inventory to setup the Lifespan CIRR.


Organization
------------------

### diana module

- `utils` contains generic code with no references to diana-dixels or endpoints.
- `apis` contains get/put/handle functions for dixels and endpoints
- `daemon` contains some higher level repeating tasks like file monitoring
- `star` overloads apis with a celery-friendly wrapper function (something like 
  `do-star(object, func, item)`)
  
### guidmint module

- implements "mints" for generating repeatable global uids and sham names/dobs

### apps

- `diana-worker` creates a celery worker for the diana-star app
- `get-a-guid` is a REST API for `guidmint`
- `radcatr` is a TKL UI for diana-style report review and annotation
- `utils` contains CLI wrappers for common diana functions such as querying endpoints and saving images
  
### stack


  
### docker

- Container descriptions (dockerfiles) for `diana-worker` and a release build of `orthanc` for Debian.  
  These containers are built for both amd64 and armv7 architectures on travis as part of testing, so they are always available from docker hub at `derekmerck/diana-worker` and `derekmerck/orthanc` respectively.
  
  
Unit Tests
------------------

The service stack can be tested by setting up a testbench with vagrant, as described above.

Some simple, anonymized DICOM files are included to test apis for upload, download,
caching, etc.


