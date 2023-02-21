# Gavanalyser Development Guide

## Project Folder Structure

Below is a tree diagram of the folder structure of this project and a short description of what is in each folder.
```
├── .env -- configuration environment variables for the server
├── docker-compose.yml -- docker-compose file for production
├── backend/ -- The flask backend and harvester code
│   ├── Dockerfile -- docker file for production and development
│   ├── galvanalyser/ -- Library files for interacting with the database
│   │   ├── database/ -- SQLAlchemy and psycopg2 code for interfacing with the database
│   │   ├── harvester/ -- harvester code for monitoring, parsing and uploading dataasets
│   └── test/ -- unit and integration tests for backend and harvester code
├── docs/ -- documentation
└── frontend/ -- The react frontend code
    ├── Dockerfile -- docker file for production
    ├── Dockerfile_dev -- docker file for development
    └── src/ -- source code for react components and app
```### Create initial galvanalyser database:

```bash
docker-compose run --rm app python manage.py create_db
```

## Common actions

### Create a harvester user (can be shared amongst particular machines)

There is normally only a single harvester user account, which is used by the backend 
server to run harvesters, and which is created by the `create_db` command 
using the information in the `.env` file. However, there is also the possibility to run 
harvesters not part of the main backend server (i.e. on a tester machine), and this 
command will create new harvester users for this purpose.

```bash
docker-compose run --rm app python manage.py create_harvester
```

Options:
- `--harvester`
- `--password`


### Run backend tests (including harvester code)

The test-suite runs over a set of battery tester files in the directory specified by 
`GALVANALYSER_HARVESTER_TEST_PATH`

```bash
docker-compose run --rm app python manage.py test
```


### To run the entire stack for development

Create a `docker-compose.override.yml` file in the root directory next to `docker-compose.yml`.
Put the following in there:

```yaml
version: "2"
services:
  frontend:
    image: frontend_dev
    build:
      dockerfile: Dockerfile_dev
      context: ./frontend

```

```bash
sudo docker-compose up 
```

The main difference from the production `docker-compose.yml` file is that the developer 
can edit all the code in the frontend and backend files, and this will automatically 
compile and restart the dockerised frontend and backend servers appropriately, useful in 
development.
