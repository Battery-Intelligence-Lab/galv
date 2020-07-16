
# The Makefile

This project uses a Makefile to store commands used for building the project as well as several utility commands.

## make update-submodules
Checks out the git submodules or updates them if necessary.

### make format
The format script formats all the python and javascript files for consistent formatting

### make builder-docker-build
This builds the "builder" docker image. This is a docker image that can be used for cross platform building of this project.

### make builder-docker-run
This runs the builder docker image. It mounts the project directory in the builder docker container and the builder docker then runs the builder/build.sh script. This should generate the protobuf and library files used by the project in the appropriate places in this project
on your local file system.

### make protobuf
This builds the protobuf files for javascript and python.
It also bundles up some JS modules and the built javascript protobufs into a single file to be served to web clients.

### make harvester-docker-build
Builds the harvester docker image

### make harvester-docker-run
Runs the harvester docker image. The paths in this will need to change since there are a couple of absolute ones to directories on my machine.

### make test
Runs some old broken tests. It'd be good to fix this some time.

### make init
pip installs the python requirements. See Setup.