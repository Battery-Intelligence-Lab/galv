to create initial redash database:

```bash
sudo docker-compose run --rm server create_db
```

to create initial galvanalyser database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_db
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
docker-compose run --rm galvanalyser_app python manage.py add_harvester_path
```

to run:

```bash
sudo docker-compose up -d
```
