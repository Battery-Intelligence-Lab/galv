# Galvalanyser Administration

This guide assumes you have a Galvanalyser server setup.

## User roles

There are two types of users in galvanalyser:
1. The first are standard user accounts, that are used for authentication on the 
   frontend, and the REST API. 
2. The second are harvester user accounts. Ordinarily, there is only one harvester user 
   account, and the username and password for this account is set in the `.env` file in 
   the server. This account is a postgres account on the database, and the harvesters 
   use this account to upload data directly to the database.


## Creating users

User accounts can be added using the `docker-compose` CLI interface. The command for 
creating a new user is:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_user
```

## Configuring harvesters

Harvesters are created and configured via the frontend web application
