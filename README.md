# Galvanalyser project

Galvanalyser is a system for automatically storing data generated by battery cycling 
machines in a database, using a set of "harvesters", whose job it is to monitor the 
datafiles produced by the battery testers and upload it in a standard format to the 
server database. The server database is a relation database that stores each dataset 
along with information about column types, units, and other relevant metadata (e.g. cell 
information, owner, purpose of the experiment)

There are two user interfaces to the system:
- a web app front-end that can be used to view the stored datasets, manage the 
  harvesters, and record metadata for each dataset
- a REST API which can be used to download dataset metadata and the data itself. This 
  API conforms to the [battery-api](https://github.com/martinjrobins/battery-api) 
  OpenAPI specification, so tools based on this specification (e.g. the Python client) 
  can use the API.
  
A diagram of the logical structure of the system is shown below. The arrows indicate the 
direction of data flow.
![The logical relationship of the various Galvanalyser components](./documentation/GalvanalyserStructure.PNG)

## Project documentation

The `documentation` directory contains more detailed documentation on a number of topics. It contains the following items:
* [FirstTimeQuickSetup.md](./docs/FirstTimeQuickSetup.md) - A quick start guide to 
  setting up your first complete Galvanalyser system
* [AdministrationGuide.md](./docs/AdministrationGuide.md) - A guide to performing 
  administration tasks such as creating users and setting up harvesters
* [DevelopmentGuide.md](./docs/DevelopmentGuide.md) - A guide for developers on 
  Galvanalyser
* [ProjectStructure.md](./docs/ProjectStructure.md) - An overview of the project folder 
  structure to guide developers to the locations of the various parts of the project

## Technology used

This section provides a brief overview of the technology used to implement the different parts of the project.

### Docker

Dockerfiles are provided to run all components of this project in containers. A docker-compose file exists to simplify starting the complete server side system including the database, the web app and the Nginx server. All components of the project can be run natively, however using Docker simplifies this greatly.

A Docker container is also used for building the web app and its dependencies to simplify cross platform deployment and ensure a consistent and reliable build process.

### Backend server

The server is a [Flask](flask.palletsprojects.com) web application, which uses 
[SQLAlchemy](https://www.sqlalchemy.org/) and [psycopg2](https://www.psycopg.org/) to 
interface with the Postgres database.

### Harvesters 

The harvesters are python modules in the backend server which monitor directories for 
tester datafiles, parse them according to the their format and write the data and any 
metadata into the Postgres database. The running of the harvesters, either periodically 
or manually by a user, is done using a [Celery](https://docs.celeryproject.org/) 
distributed task queue.

### Frontend web application

The frontend is written using javascript, the [React](https://reactjs.org/) framework 
and using [Material-UI](https://material-ui.com/) components.


### Database

The project uses PostgreSQL for its database. Other databases are currently not 
supported. An entity relationship diagram is shown below.
![Galvanalyser entity relationship diagram](./documentation/Galvanalyser_DB_ERD.png)
