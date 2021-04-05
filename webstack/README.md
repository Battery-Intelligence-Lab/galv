to install:


```bash
sudo docker-compose run --rm server create_db
```
or

```bash
docker-compose run --rm galvanalyser_app python manage.py create_redash_db
docker-compose run --rm server ./manage.py database reencrypt <old_secret> 
<new_secret>
```

```bash
docker-compose run --rm galvanalyser_app python manage.py create_galvanalyser_db
docker-compose run --rm galvanalyser_app python manage.py create_user
docker-compose run --rm galvanalyser_app python manage.py create_institution
docker-compose run --rm galvanalyser_app python manage.py create_harvester
docker-compose run --rm galvanalyser_app python manage.py create_machine_id
docker-compose run --rm galvanalyser_app python manage.py add_machine_path
```




to create initial redash database:

```bash
sudo docker-compose run --rm server create_db
```

to create initial galvanalyser database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_galvanalyser_db
```

to create initial redash database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_redash_db
```

reencrypt redash after changes to REDASH_SECRET_KEY

```bash
docker-compose run --rm server ./manage.py database reencrypt <old_secret> <new_secret>
```

to create a user:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_user
```

to create an institution:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_institution
```

to create a harvester user (can be shared amongst particular machines):

```bash
docker-compose run --rm galvanalyser_app python manage.py create_harvester
```

to create a machine:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_machine_id
```

to add a path to a machine:

```bash
docker-compose run --rm galvanalyser_app python manage.py add_machine_path
```

to test the harvester code:

```bash
docker-compose run --rm galvanalyser_app python manage.py test_harvester
```

to test the api code:

```bash
docker-compose run --rm galvanalyser_app python manage.py test_api
```

to run the stack:

```bash
sudo docker-compose up -d
```

to backup the redash dbase:

```bash
pg_dump -Fc -p 5432 -h localhost -U postgres -f redash_backup.sql postgres 
```
