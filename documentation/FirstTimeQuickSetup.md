
# First Time Quick Setup

This section describes the command line commands you will need to run to set up the 
system for the first time. It is assumed you are logged into the server machine that you 
wish to use, using the user account that you want to run the server with 

The steps below have been tested in a bash shell on a server running Ubuntu. The entire 
application has been dockerised, so can in theory be used on other operating systems 
with minimal modification. However, the `crontab` and `systemd` instructions below are 
specific to the Linux operating system.

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

Open the `webstack/.env` file. This file specifies the options that you can use to setup 
your Galvanalyser installation, such as passwords and data locations. Comments in the 
file give more detailed information on each option. Please go through each option and 
edit to your desired configuration.


## Setting up the Galvanalyser database

Installation and administration of galvanalyser is done using a command line interface 
(cli) that you can run via `docker-compose`. Change directory to the `webstack`
directory and run the following command to create the galvanalyser database tables. 

**Note**: *when this command is run, it will drop all tables from the current database, 
so if you have existing data it will be deleted.*

```bash
docker-compose run --rm galvanalyser_app python manage.py create_galvanalyser_db
```

Now you can create a user account. This creates a read-only postgres user that can be 
used to connect to the galvanalyser postgres database. The redash web app can use this 
user to create a data source that can be shared amongst many redash user accounts. 

```bash
docker-compose run --rm galvanalyser_app python manage.py create_user
```

The next step is to create a harvester account. This creates a postgres user that can 
upload datasets to the galvanalyser database. This account is used by the harvesters. 

```bash
docker-compose run --rm galvanalyser_app python manage.py create_harvester
```

Each harvester account can be used by multiple harvester machines. To create a new 
machine, use the `create_machine_id` command. 

```bash
docker-compose run --rm galvanalyser_app python manage.py create_machine_id
```

Each machine can scan multiple directories for new battery tester files. To add a new 
directory, you can use the `add_machine_path` command. This will prompt for a directory 
name to be scanned. Please enter in a relative directory name that is relative to the
`GALVANALYSER_HARVESTER_BASE_PATH` option in the `.env` file, without the leading slash. 
For example, if your `GALVANALYSER_HARVESTER_BASE_PATH` is set to `/home/galv/datafiles` 
and you want to add the directory `/home/galv/datafiles/harvester1/machine2`, then you 
would enter `harvester1/machine2` here. Note that you cannot use wildcard characters to 
scan multiple directories, for example `harvester1/*` will not work.

If you wish to move this base path once galvanalyser is installed, just edit the 
`GALVANALYSER_HARVESTER_BASE_PATH` option and move your files to the new location. For 
example, if you later change `GALVANALYSER_HARVESTER_BASE_PATH` to 
`/home/galv/new_datafiles`, then using the example in the preceeding paragraph, the 
directory that will be scanned by this machine will now be 
`/home/galv/new_datafiles/harvester1/machine2`.

```bash
docker-compose run --rm galvanalyser_app python manage.py add_machine_path
```

Finally, to run a harvester machine you need to provide an institution, the following 
command will allow you to add a new institution.

```bash
docker-compose run --rm galvanalyser_app python manage.py create_institution
```

## Running server harvesters

Following the commands in the previous section will setup the initial galvanalyser 
database and create the necessary user, harvester accounts, and harvester machines. Now 
you can start running the harvester machines. You can manually run a harvester machine 
using the following command (once again, this should be run from the `webstack` 
directory)

```bash
docker-compose run --rm galvanalyser_app python manage.py run_harvester
```

This will prompt for a harvester account username and password, a machine id and an 
institution. It will then run the specified harvester machine, which will scan the 
directories that you have added for that machine.

The harvester machines are designed to be periodically run, so for long-term use you 
should setup a periodic job on the server machine to run the harvester (using the 
command above). On Unix server machines you can setup a periodic cron job using the 
`crontab` command, and you can see help and examples of use 
[here](https://www.computerhope.com/unix/ucrontab.htm), as well as a useful web app for 
constructing crontab schedules [here](https://crontab.guru/). This is an example of a 
crontab entry that you might setup to run a harvester, which runs a script 
`run_harvester.sh` from the webstack folder on the 0th minute of every hour:

```cron
0 * * * * cd /home/galvanalyser/galvanalyser/webstack && run_harvesters.sh 
```

`run_harvester.sh` is a shell script in the `webstack` sub directory that runs all the 
harvester machines specified. You can see an example of this script at 
`webstack/runrun_harvesters.sh`, which you can edit to include the harvester accounts 
and machine ids that you have created.

## Running galvanalyser server

You can run the galvanalyser server and the redash instance using the following 
`docker-compose` command from the `webstack` folder.

```bash
docker-compose up
```

To run the server in detached mode (i.e. run containers in the background) using the 
`-d` option

```bash
docker-compose up -d
```

To start the server side system again after it has been stopped simply run 
`docker-compose up` in the `webstack` directory.

A template SystemD service file is included in `webstack/galvanalyser.service` that can 
be used to automatically start the server side system.


## Setting up the Redash instance

Redash is a web application that allows users to connect to a postgres database (or many 
other data sources) and create queries and visualizations of the data contained in the 
database. A redash instance is bundled with galvanalyser, allowing you to use redash to 
view the battery datasets you have uploaded to the galvanalyser database. You are free 
to use redash in anyway you wish, although we have an initial redash setup for you to 
use and customise. You can find more information about redash in general at their 
[website](https://redash.io/).

To setup the initial redash database, you can run the following command:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_redash_db
```

The `REDASH_SECRET_KEY` environment variable used to create the initial redash database 
is probably different to the one you have used, so you also need to reencrypt the data 
in the initial redash database. You can do this using the following command:

```bash
docker-compose run --rm server ./manage.py database reencrypt <old_secret> <new_secret>
```

where `old_secret` is the value of `REDASH_SECRET_KEY` in the example `.env` file 
(currently "redash_test_secret_key"), and `new_secret` is the value of 
`REDASH_SECRET_KEY` that you have used.

Once you have done this, make sure the galvanalyser stack is up and running using 
`docker-compose up`, then navigate your browser to [localhost:5000](localhost:5000), 
where you should see the redash login page. You can login using the default admin 
account, which has email `admin@not.a.real.domain.org`, username `admin` and password 
`admin99`. Note that admin and user accounts for redash are *only* for redash and are 
*different* from the user and harvester accounts you have already created for the 
galvanalyser database.

**Note**: *once you have logged into redash you should change at least the username and 
password for the admin user to custom values*.

As an admin account, you can then create normal user accounts for other redash users. 
The initial redash database has a user group called `oxford` that contains a 
*data source* that connects to the galvanalyser database. You should edit the options 
for this data source (go to profile->Data_Sources->galvanalyser), and change the 
username and password for the database connection to the galvanalyser user username and 
password that you created with the `docker-compose` `create_user` command. When you add 
new users to redash, make sure to add them to the `oxford` group (or other groups that 
you create) that contains the relevant connection to the galvanalyser database.

Once you have set the correct password to connect to the galvanalyser database, you 
should be able to navigate to the redash dashboards (start with the `datasets` 
dashboard) to view the datasets in the galvanalyser database.
