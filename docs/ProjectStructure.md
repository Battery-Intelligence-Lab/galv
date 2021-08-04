# Galvanalyser project Folder Structure

Below is a tree diagram of the folder structure of this project and a short description of what is in each folder.
```
├── .env -- configuration environment variables for the server
├── .docker-compose.yml -- docker-compose file for production
├── .docker-compose.dev.yml -- docker-compose file for development
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
```
