
# First Time Quick Setup

This section describes the command line commands you will need to run to set up the system for the first time. It is assumed you have `make`, `docker` and `docker-compose` installed, if you don't you will need to install them and have them available in you command line. The commands listed in this section assume your terminal is in the root directory of this project (the one that contains the `Makefile`).

## Setting up the server based components

This section describes how to setup and run the server side components of the Galvanalyser system. These include the database and the web app.

### Downloading dependencies

This project uses git submodules to increase modularity and to include dependencies. The first thing you will need to do is download the submodules. Running the following command will achieve that.
```
# Download the submodules
make update-submodules
```

### Building the project

This project uses a docker container to run its build environment to enable cross platform builds and to ensure a consistent and reliable build environment. In order to build this project you will first need to build the builder docker image with the following command.
```
# Build the builder docker image
make builder-docker-build
```
Now that the builder image has been built you can run the build process with the following command. If you change parts of this project that require compilation you can run this command again to rebuild it.
```
# Build the webstack
make build-webstack
```

### Configuring the system for running for the first time

Next you will need to configure where the postgres docker stores the database data. You do this by editing the value assigned to `PG_DATA_PATH` in the file `webstack/.env`
```
# Example content of the webstack/.env
PG_DATA_PATH=/path/to/your/postgres/data/directory
```
When you run the postgres docker container and its data directory is empty it will perform some initial setup steps. In order to set a password for the postgres super user account of the database it is necessary to edit the `webstack/docker-compose.yaml` file to add a `POSTGRES_PASSWORD` environmental variable to specify the password for the user. This value can be removed from the file once the postgres docker container has performed its initial setup when run with an empty data directory. The section of the `webstack/docker-compose.yaml` file you need to edit looks like this:
```
  postgres:
    image: "postgres"
    stop_signal: SIGINT                 # Fast Shutdown mode
    ports:
      - "5432:5432"
```
Change it to include an environmental variables section that specifies the `POSTGRES_PASSWORD` value like this:
```
  postgres:
    image: "postgres"
    environment:
      POSTGRES_PASSWORD: your_postgres_user_password_here
    stop_signal: SIGINT                 # Fast Shutdown mode
    ports:
      - "5432:5432"
```
If desired one can add additional environmental variables to for example change the superuser account name from postgres to something else. The documentation for the postgres docker image is available [here](https://hub.docker.com/_/postgres). You can also change the port of the local machine that is mapped to the postgres database by changing the first number if the pair listed in the ports section of the `webstack/docker-compose.yaml` file.

### Running the server side system

It is now possible to start the system for the first time. This project uses docker-compose to simplify running all required components of the server side system. To start the system navigate to the webstack directory and then bring the system up with docker-compose:
```
# Next start the webstack
cd webstack
docker-compose up
```
Your terminal should now fill with the coloured log output from the three docker containers docker-compose started - the nginx web server, the postgres database, and the galvanalyser web app.

Now that the postgres container has performed its initial configuration you should remove the `POSTGRES_PASSWORD` from the `webstack/docker-compose.yaml` file.

#### Starting the server side system after it has been stopped
To start the server side system again after it has been stopped simply run `docker-compose up` in the `webstack` directory.

A template SystemD service file is included in webstack/galvanalyser.service that can be used to automatically start the server side system.

### Setting up the database

Next you will need to setup the database schema. Connect to the postgres instance you just started using your preferred postgres administration tool such as PgAdmin or psql. You will need to use the tool to run some SQL commands to set up the database. If you haven't changed the port mapping then the database should be available on your localhost on port 5432.

First create the galvanalyser database. You can do this by running the SQL commands listed in `webstack/database/create-database.pgsql`.

Next you will need to create the database schema by running all the commands listed in `webstack/database/setup.pgsql`. Your tool may allow you to run the file directly, alternativly all the commands can be simply copy-pasted into the tool.

## Setting up user accounts

To allow users to login to the web application or access the database directly they will need user accounts. The following example SQL will create user accounts for users `alice` and `bob`.
```
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
```

## Setting up the Harvesters

Once the database is set up and running and you have created your user accounts you will want to setup one or more harvesters in order to add data to the database. You may want to set up a harvester on a machine collecting active cycler data or set up one locally you can manually run to upload test files you have locally. When setting up a harvester you don't need to build the webstack or even get the submodules.

Before setting up any harvesters you will need to create a database entry describing your institution. Some example SQL is given below to do this. You will need to replace `OxfordBIL` with your institution name. This can also include your group name.
```
# Create an institution entry for your institution e.g.
INSERT INTO experiment.institution (name) VALUES ('OxfordBIL');
```
The value you choose here will be used in the harvester's configuration json file.

To set up a harvester you will need to clone this project to the machine you wish to run the harvester on if it does not already have the code. The general steps are:
1. Create a database user for the harvester
2. Create a machine_id entry for your new harvester in the database
3. Configure which directories harvester will monitor by inserting appropriate entries in the database
4. Setup the Harvester's config file
5. Run the harvester or configure the harvester to automatically run

The [AdministrationGuide.md](./AdministrationGuide.md) describes how to set up a harvester in detail, but example commands for those sections are included here for completeness.
Step 1: Create a database user for the harvester
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
Step 2: Create a machine_id entry for your new harvester in the database
```
INSERT INTO harvesters.harvester (machine_id) VALUES ('machine_name_goes_here');
```
This command will automatically create an ID number for the harvester which you will need in the next step.

Step 3: Register some directories for the harvester to monitor.
The 1 here is the id number of the harvester created earlier in the harvesters.harvester
Specify one path per row, you can specify multiple users to receive read permissions for uploaded data.
```
INSERT INTO harvesters.monitored_path (harvester_id, path, monitored_for) VALUES (1,'/usr/src/app/test-data', '{alice}');
INSERT INTO harvesters.monitored_path (harvester_id, path, monitored_for) VALUES (1,'/some/other/path/data', '{alice, bob}');
```
Step 4: Setup the Harvester's config file
Create or modify the `config/harvester-config.json` file. Here is some example content
```
{
    "database_name": "galvanalyser", 
    "database_port": 5432, 
    "database_username": "harvester_user", 
    "database_password": "harvester_password", 
    "machine_id": "test_machine_01", 
    "database_host": "127.0.0.1",
    "institution": "OxfordBIL"
}
```
Step 5: See the next section **Running the harvester**

## Running the harvester
With your database setup you can run the harvester. There are two ways you can run the harvester, you can either use a python venv or a docker image.

The harvester needs to see that a file hasn't changed in the past minute before it tries uploading it. This means that the first time you run it and for the next minute it won't actually upload anything each time you run it as it will just record the state of the file in the database.

### Running the harvester in a Docker image
To use the docker image you will need to build the image. You can use the following command line command in the root directory of this project:
```
make harvester-docker-build
```
Next you will need to edit the 'harvester-docker-run' command in the `Makefile` to mount the correct config and data directories in the docker container. The edited command should look something like
```
harvester-docker-run:
	docker run --rm -it -v /path/to/alices/data/on/machine:/usr/src/app/test-data -v /path/to/alice/and/bobs/data/on/machine:/some/other/path/data -v /path/to/direcotry/containing/config:/usr/src/app/config --net host harvester
```
The above command matches the configuration in step 3 of the **Setting up the Harvesters** section and would need to be changed appropriately. The `/path/to/direcotry/containing/config:/usr/src/app/config` is the path to the directory that contains the `harvester-config.json` file.

The harvester may then be started by running:
```
make harvester-run
```
The command stored in the `Makefile` could be run directly but storing it in the `Makefile` stores the command for future use and reduces the chance of mistyping the command when it needs to be run again.

### Running the harvester in a venv
To run in a venv first create the virtual environment if you have not already done so using the following command.
```
python3 -m venv /path/to/virtual/environment
```
Activate the virtual environment.
```
source /path/to/virtual/environment/bin/activate
```
Next install the python dependencies in the virtual environment by running:
```
make init
```
This command also installs the python dependencies for the web app components should you wish to run that in a venv instead of a docker container.

With the virtual environment active you can run the harvester by running
```
make harvester-run
```
Note in this case the harvester will be looking for its config at `./config/harvester-config.json`.

### Connecting to the database and web app
Postgres in the docker image should be accessible at localhost:5432 by default.
The webapp should be available at http://localhost:8081/ .
The webapp login details are the same as the user accounts you created in Postgres earlier.
