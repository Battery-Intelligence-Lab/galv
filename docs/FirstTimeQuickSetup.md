# First Time Quick Setup

This section describes the command line commands you will need to run to set up the 
system for the first time. It is assumed you are logged into the server machine that you 
wish to use, using the user account that you want to run the server with 

The steps below have been tested in a bash shell on a server running Ubuntu. The entire 
application has been dockerised, so can in theory be used on other operating systems 
with minimal modification. However, `systemd` instructions below are specific to the 
Linux operating system.


## Installing required tools

You need to have `docker`, `docker-compose` and `git` installed and available on your 
command-line. 

You can find installation instructions for `docker` on all major operating systems 
[here](https://docs.docker.com/engine/install/), and for `docker-compose` 
[here](https://docs.docker.com/compose/install/). For linux hosts, it is useful to be 
able to use `docker` as a non-root user, and you can find instructions on how to set 
this up [here](https://docs.docker.com/engine/install/linux-postinstall/). If you don't, 
note that you will need to add `sudo ...` in front of every `docker` and 
`docker-compose` command listed below.

Installation instructions for `git` for all major OSs can be found 
[here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Get the galvanalyser source code

First you will need to clone the galvanalyser repository using `git`:

```bash
git clone https://gitlab.com/battery-intelligence-lab/galvanalyser-project/galvanalyser.git
cd galvanalyser
```

## Setup global environment variables

Open the `.env` file in the root of the repository. This file specifies the options that 
you can use to setup your galvanalyser installation, such as passwords and data 
locations. Comments in the file give more detailed information on each option. Please go 
through each option and edit to your desired configuration.

## Building docker images (only when upgrading to a new version of galvanalyser)

If you have previously installed and run galvanalyser you might already have old docker 
images already built. To rebuild the images, run the following command:

```bash
docker-compose build
```

## Setting up and creating user accounts on the galvanalyser database

Installation and administration of galvanalyser is done using a command line interface 
(cli) that you can run via `docker-compose`. Change directory to the root of the repository 
and run the following command to create the galvanalyser database tables. 

**Note**: *when this command is run, it will drop all tables from the current database, 
so if you have existing data it will be deleted.*

```bash
docker-compose run --rm app python manage.py create_db
```

Now you can create one or more user accounts. Create one user account for each user you 
want to be able to login to the galvanalyser web application. Access permissions on each 
dataset stored in galvanalyser give access only to certain user accounts.

```bash
docker-compose run --rm app python manage.py create_user
```

# Running Galvanalyser

You can run the galvanalyser server and web application frontend using the following 
`docker-compose` command from the root folder of the repository.

```bash
docker-compose up
```

Now view the 'localhost' IP address [http://127.0.0.1/](http://127.0.0.1/) in your 
browser and you should see the Galvanalyser login page. If you wish to use the frontend 
from another machine, use the IP address or URL of the server instead. 

Use one of the user accounts you created earlier to log-in to the frontend.

To run the server in detached mode (i.e. run containers in the background) using the 
`-d` option

```bash
docker-compose up -d
```

To start the server side system again after it has been stopped simply run 
`docker-compose up` in the root folder.

A template SystemD service file is included in the repository root directory 
`galvanalyser.service` that can be used to automatically start the system.
