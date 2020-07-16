
# First Time Quick Setup
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
    "database_host": "127.0.0.1",
    "institution": "Oxford"
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

## Setting up for the first time
The following are some example commands you'd need to run to get started. This assumes you have `make`, `docker` and `docker-compose` installed
```
# Download the submodules
make update-submodules

# Build the builder docker image
make builder-docker-build

# Build the webstack
make build-webstack

# Configure where the postgres docker stores the data by editing PG_DATA_PATH in webstack/.env

# Next start the webstack
cd webstack
docker-compose up

# Now connect to the database and use the following to set it up
# Create the galvanalyser database with the 'CREATE DATABASE' statement at the start of webstack/database/setup.pgsql
# Run all the sql after the 'CREATE DATABASE' statement in that file in the galvanalyser database.

# Now setup the following as appropriate to your setup.

# Create one or more harvester users as described in the 'Harvester config' section above.

# Add one or more harvesters to the harvesters table. The names given should match the name you use in the harvester config.
# Here we're using 'test_machine_01' to match the name in the 'Harvester config' section above.
INSERT INTO harvesters.harvester (machine_id) VALUES ('test_machine_01');

# Create an institution entry for your institution e.g.
INSERT INTO experiment.institution (name) VALUES ('Oxford');
# The name you use should match the name in your harvester config json files

# Create some accounts for the users of the application
CREATE USER alice WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  PASSWORD 'alice_pass';
GRANT normal_user TO alice;

CREATE USER bob WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  PASSWORD 'bob_pass';
GRANT normal_user TO bob;

# Register some directories for the harvester to monitor.
# The 1 here is the id number of the harvester created earlier in the harvesters.harvester
# Specify one path per row, you can specify multiple users to receive read permissions for uploaded data
INSERT INTO harvesters.monitored_path (harvester_id, path, monitored_for) VALUES (1,'/usr/src/app/test-data', '{alice}');
INSERT INTO harvesters.monitored_path (harvester_id, path, monitored_for) VALUES (1,'/some/other/path/data', '{alice, bob}');

# With your database setup you can run the harvester.
# You can setup the harvester on another machine in which case you don't need to build the webstack or even get the submodules.
# You only need to setup the harvester-config.json and the following.
# There are two ways you can run the harvester, you can either use a python venv or a docker image.

# To use the docker image
make harvester-docker-build
# Edit the 'harvester-docker-run' command in the make file to mount the correct config and data directories in the docker container and then run it with
make harvester-run

# To run in a venv use
make init
make harvester-run
# Note in this case the harvester will be looking for its config at ./config/harvester-config.json 

# The harvester needs to see that a file hasn't changed in the past minute before it tries uploading it.
# This means that hte first time you run it and for the next minute it won't actually upload anything each time you run it as it will just record the state of the file in the database.

```

## Connecting to things
Postgres in the docker image should be accessible at localhost:5432 as usual.
The webapp should be available at http://localhost:8081/ .
The webapp login details are the same as the user accounts you created in Postgres earlier.