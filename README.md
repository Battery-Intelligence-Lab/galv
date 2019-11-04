# Galvanalyser project

Folder Structure
----------------
```
├── config -- Has an example harvester config in, can be used to store test harvester configs locally
├── galvanalyser -- The python code goes here, all under the galvanalyser namespace
│   ├── database -- Library files for interacting with the database
│   ├── harvester -- The harvester app
│   ├── protobuf -- Automatically generated protobuf python code
│   └── webapp -- The webapp
│       ├── assets -- Static files here are served by the webapp. The JS files that handle dash callbacks client side are here
│       ├── datahandling -- Python flask route handlers for handling requests to query the database
│       └── pages -- Files describing the webapp pages
├── harvester -- Harvester docker file
├── libs -- assorted dependency libraries
│   ├── closure-library -- google library, used for building the single js file for protobufs and dependencies, provides AVL Tree data structure
│   ├── galvanalyser-js-protobufs  -- Automatically generated protobuf javascript code
│   └── protobuf -- google protobuf library
├── protobuf -- definition of the protobufs used in this project
├── tests -- Tests (these are old and may not work anymore and aren't proper unit tests)
├── webapp-static-content -- Static content
│   ├── js -- The js file here gets bundled into the file generated by the closure-library
│   └── libs -- The automatically generated js file made by closure-library gets put here. This is served by nginx
└── webstack -- Docker-compose things go here
    ├── dashapp -- The dockerfile for the web app
    ├── database -- The sql file for setting up the database (should probably move elsewhere)
    └── nginx-config -- The nginx config file lives here
```
## The Makefile
There are several scripts in the Makefile that are useful

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

## Setup
If you want to run things locally - not in a docker
```
# make a virtual environment
python3 -m venv ./.venv
# run the init script in the Makefile to pip install all the requirements
make init
```

## Running the server
In the `webstack` directory run `docker-compose up`

## Database setup
There is a file `webstack/database/setup.pgsql` that describes the database

## Harvester config
For the harvester that runs in a docker you can create a `harvester-config.json` file in the `config` directory with some content that looks like
```
{
    "database_name": "galvanalyser", 
    "database_port": 5432, 
    "database_username": "harvester_user", 
    "database_password": "harvester_password", 
    "machine_id": "test_machine_01", 
    "database_host": "127.0.0.1"
}
```
You'll want to add a harvester user to the database
```
CREATE USER harvester_user WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  PASSWORD 'harvester_password';

GRANT harvester TO harvester_user;
```
