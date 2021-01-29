to create initial redash database:

```bash
sudo docker-compose run --rm server create_db
```

to create initial galvanalyser database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_db
```

to run:

```bash
sudo docker-compose up -d
```
