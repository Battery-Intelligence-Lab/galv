from flask.cli import FlaskGroup
from galvanalyserapp.database import create_database
import psycopg2
from app import app, config

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    create_database(config)

if __name__ == "__main__":
    cli()
