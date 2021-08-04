### Create initial galvanalyser database:

```bash
docker-compose run --rm galvanalyser_app python manage.py create_galvanalyser_db
```


### Create a harvester user (can be shared amongst particular machines)

```bash
docker-compose run --rm galvanalyser_app python manage.py create_harvester
```

Options:
- `--harvester`
- `--password`


### Run backend tests (including harvester code)

The test-suite runs over a set of battery tester files in the directory specified by 
`GALVANALYSER_HARVESTER_TEST_PATH`

```bash
docker-compose run --rm galvanalyser_app python manage.py test
```


### To run the entire stack for development

```bash
sudo docker-compose -f docker-compose.dev.yml up ```
