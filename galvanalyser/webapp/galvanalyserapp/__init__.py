import os
import flask
from flask_login import current_user
import psycopg2
from urllib.parse import urlparse

def init_db():

    redash = urlparse(os.getenv('REDASH_DATABASE_URL'))
    config = {
        "db_conf": {
            "database_name": "galvanalyser",
            "database_port": 5433,
            "database_host": "galvanalyser_postgres",
            "database_user": "postgres",
            "database_pwd": os.getenv('POSTGRES_PASSWORD'),
            "redash_name": redash.path[1:],
            "redash_port": redash.port,
            "redash_host": redash.hostname,
            "redash_user": redash.username,
            "redash_pwd": redash.password,
            "redash_url": os.getenv('REDASH_DATABASE_URL'),
        },
        "default_harvester": {
            "name": os.getenv("GALVANALYSER_HARVESTER_NAME"),
            "pwd": os.getenv("GALVANALYSER_HARVESTER_PWD"),
            "machine_id": "server",
            "base_path": "/usr/data",
            "institution": os.getenv("GALVANALYSER_HARVESTER_INSTITUTION"),
        },
        "default_user": {
            "name": os.getenv("GALVANALYSER_USER_NAME"),
            "pwd": os.getenv("GALVANALYSER_USER_PWD"),
        }
    }

    def get_redash_db_connection():
        return psycopg2.connect(
            host=config["db_conf"]["redash_host"],
            port=config["db_conf"]["redash_port"],
            database=config["db_conf"]["redash_name"],
            user=config["db_conf"]["redash_user"],
            password=config["db_conf"]["redash_pwd"],
        )

    def get_db_connection_for_superuser():
        print('password is ',os.getenv('POSTGRES_PASSWORD'), 'or',
              config["db_conf"]["database_pwd"])
        return psycopg2.connect(
            host=config["db_conf"]["database_host"],
            port=config["db_conf"]["database_port"],
            database=config["db_conf"]["database_name"],
            user=config["db_conf"]["database_user"],
            password=config["db_conf"]["database_pwd"],
        )

    def get_db_connection_for_current_user():
        username, password = current_user.id.split(":", 1)
        return psycopg2.connect(
            host=config["db_conf"]["database_host"],
            port=config["db_conf"]["database_port"],
            database=config["db_conf"]["database_name"],
            user=username,
            password=password,
        )

    def get_current_user_name():
        username, password = current_user.id.split(":", 1)
        return username

    config[
        "get_db_connection_for_current_user"
    ] = get_db_connection_for_current_user
    config[
        "get_db_connection_for_superuser"
    ] = get_db_connection_for_superuser
    config[
        "get_redash_db_connection"
    ] = get_redash_db_connection

    config["get_current_user_name"] = get_current_user_name
    return config


def init_app(config):
    app = flask.Flask(__name__)

    # TODO read this from an external file
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass



    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

    return app

