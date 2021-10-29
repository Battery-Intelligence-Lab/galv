# Galvalanyser Administration

This guide assumes you have a Galvanalyser server setup.

## User roles

There are two types of users in galvanalyser:
1. The first are standard user accounts, that are used for authentication on the 
   frontend, and the REST API. Users can optionally belong to an Admin group, which 
   allows them more permissions in terms of viewing and editing dataset metadata, and 
   allows for setting up and altering harvester schedules and directories.
2. The second is the harvester user account. Ordinarily, there is only one harvester 
   user account, and the username and password for this account is set in the `.env` 
   file in the server. This account is a postgres account on the database, and the 
   harvesters use this account to upload data directly to the database.


## Creating users

User accounts can be added using the `docker-compose` CLI interface. The command for 
creating a new user is:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_user
```

You will be promoted for a username, password and email for the new user, and asked if 
this user should belong to the Admin group

## Configuring harvesters

Harvesters are created and configured via the frontend web application, and only by 
users that belong to the Admin group.

First navigate to the harvester page (the cloud upload icon in the left hand side 
drawer). Here you are presented with an (initially empty) table of harvester machines. 
Add a new machine using the "plus" button and fill in a name. Click the save button 
(disk icon) to save your new name.

Click on your new harvester and you will be presented with an (initially empty) list of 
paths to monitor. The base path should correspond with the 
GALVANALYSER_HARVESTER_BASE_PATH environment variable that you set in the `.env` file. 
Use the "plus" button to add a new path and edit it to the directory that you wish to 
monitor.

Now that you have a harvester and a path to monitor, click on the harvester and click 
the "play" button to run it. While the harvester is running, the "Is Running" column 
will indicate this, and once it has completed the "Last Completed Run" will record the 
last time the harvester ran to completion. If you wish to run the harvester periodically 
then enter a number in the "Periodic Hour" column. This correspond to the hour of the 
day that you wish the harvester to run in 24 hour time, so for example if you enter in 
"1", then the harvester will be run every day at 1am.

Once you have run your new harvester, you can click on each monitored path to see a list
of the files that have been found in each path, as well as their current status.
