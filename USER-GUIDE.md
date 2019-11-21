# Galvalanyser Administration
This guide assumes you have a Galvanalyser server setup and you have a user account with permissions to create database users.
You will also need to know the address of the server and the port postgres is listening on.

## User roles
Two roles (similar to user groups) should already exist in a postgres server which has been setup with the galvanalyser database structure. These two roles are `normal_user` and `harvester`.

### normal_user
Users who are assigned this role will be able to see datasets and data that they are allowed to see. Anyone who is meant to use the galvanalyser app should be assigned this role.

### harvester
This role should be assigned to accounts that are used by harvesters to upload data.

## Creating users
User accounts for the galvanalyser app are created by creating users in postgres and assigning them the `normal_user` role. Users should be assigned a password.

There are many GUI and commandline tools for interacting with postgres servers. PgAdmin is one such GUI tool and it provides a GUI to create login roles. There is documentation elsewhere on the internet describing how to do so. If you wish to use SQL to create users, the README for this project includes example SQL commands to create users called `alice` and `bob` in the `Setting up for the first time` section.

## Creating harvester database credentials
Creating accounts to let harvesters connect to the database is done exactly the same way as creating users except that instead of assigning the account the `normal_user` role they are assigned the `harvester` role.

## Configuring harvesters (database)

### Creating a harvester
Once you have created some login credentials for the harvester you will need to create an entry in the `harvester` table in the `harvesters` schema. An id number will automatically be created so you only need to provide a unique name for the harvester. GUI postgres tools should let you do this through a GUI. If you wish to use SQL you will use a command similar to
```
INSERT INTO harvesters.harvester (machine_id) VALUES ('machine_name_goes_here');
```

### Configuring monitored directories
The directories the harvesters monitor are configured in the `monitored_path` table in the `harvesters` schema. You will need to know the id number for the particular harvester you wish to configure. The id number is stored in the `harvester` table in the `harvesters` schema. A GUI tool will let you look at the data in the table. You could also use an SQL query like the following to find it
```
SELECT id FROM harvesters.harvester WHERE machine_id=('machine_name_goes_here')
```
Once you know the id number you can create rows in the `monitored_path` table - one row per path to monitor. Each row includes the `harvester_id` number of the harvester that is monitoring it; the `path` that is to be monitored; and an array of 0 or more users who the directory is `monitored_for`. The entries in the `monitored_for` field should match the user names of postgres user accounts with the `normal_user` role. When the harvester with the id specified in the row harvests data from directory specified in the row it will automatically grant permission for the users specified in the row to view the harvested data. If you are using SQl to create the rows you would use something that looks like this
```
INSERT INTO harvesters.monitored_path (harvester_id, path, monitored_for) VALUES (1,'/example/directory/', '{alice, bob}');
```
That would tell the harvester with the id number `1` to monitor `/example/directory/` and to give read permission to all data it harvests from there to the users `alice` and `bob`.

Existing rows in the `monitored_path` table can be modified but changing which users have access to data from a particular directory won't update the permissions for already uploaded data.

## Changing user dataset access
The table that controls which users have permissions to see which datasets is the `access` table in the `experiment` schema. If you wish to grant new users permissions to see existing datasets or revoke permissions to see existing datasets then you will need to create or delete rows from this table. Each row in this table contains a `dataset_id` number that uniquely identifies a dataset and a `user_name` that identifies a users. Each row grants the user named in tht row permission to see the dataset named in that row.
When adding or removing rows you will need to know the `dataset_id` number for the dataset you wish to grant or revoke permissions for. That can be found in the `id` column in the `dataset` table in the `experiment` schema.