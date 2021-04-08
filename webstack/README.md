### Create initial redash database

```bash
sudo docker-compose run --rm server create_db
```

### Create initial galvanalyser database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_galvanalyser_db
```

### Restore redash database

Uses copy of database stored at 
`galvanalyser/webapp/galvanalyserapp/database/redash_backup.sql`

```bash
docker-compose run --rm galvanalyser_app python manage.py create_redash_db
```

Normally followed by a reencrypt as below

### Reencrypt redash after changes to REDASH_SECRET_KEY

```bash
docker-compose run --rm server ./manage.py database reencrypt <old_secret> <new_secret>
```

where `old_secret` is "redash_test_secret_key" if you have just restored from the 
default redash database above


### Create a galvanalyser database user:

Creates a read-only database user, for connecting a redash data_source

```bash
docker-compose run --rm galvanalyser_app python manage.py create_user
```

Options:
- `--username`
- `--password`

### Create an institution:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_institution
```

Options:
- `--name`

### Create a harvester user (can be shared amongst particular machines)

```bash
docker-compose run --rm galvanalyser_app python manage.py create_harvester
```

Options:
- `--harvester`
- `--password`


### Create a machine

```bash
docker-compose run --rm galvanalyser_app python manage.py create_machine_id
```

Options:
- `--machine_id`

### Add a path to a machine

This adds a path to a machine. The machine will scan this path for new battery tester 
files. 

For harvesters that are run in a docker containers (either as part of the server 
docker-compose, or independently in their own docker container), this path should be 
relative to the `GALVANALYSER_HARVESTER_BASE_PATH` directory.

Each path is associated with a given `user`, and all files uploaded from the path are 
able to be read by that `user`.

```bash
docker-compose run --rm galvanalyser_app python manage.py add_machine_path
```

Options:
- `--machine_id`
- `--path`
- `--user`

### Test the harvester code

The test-suite runs over a set of battery tester files in the directory specified by 
`GALVANALYSER_HARVESTER_TEST_PATH`

```bash
docker-compose run --rm galvanalyser_app python manage.py test_harvester
```

### Test the database API code

```bash
docker-compose run --rm galvanalyser_app python manage.py test_api
```

### To run the entire stack

```bash
sudo docker-compose up -d
```

### Backup the redash database

```bash
pg_dump -Fc -p 5432 -h localhost -U postgres -f redash_backup.sql postgres 
```


### Run a harvester

```bash
docker-compose run --rm galvanalyser_app python manage.py test_api
```

Options:
- `--harvester`
- `--password`
- `--machine_id`
- `--institution`
