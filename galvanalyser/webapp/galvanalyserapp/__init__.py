import os
import flask
from flask_login import current_user
import psycopg2

def init_app():
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

    config = {
        "db_conf": {
            "database_name": "galvanalyser",
            "database_port": 5432,
            "database_host": "postgres",
        }
    }

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
    config["get_current_user_name"] = get_current_user_name

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import Dash application
        from .dashboard import create_dashboard
        app = create_dashboard(app, config)

        return app

    return app

