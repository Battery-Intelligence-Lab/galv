to create initial redash database:

```bash
sudo docker-compose run --rm server create_db
```

to create initial galvanalyser database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_db
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
