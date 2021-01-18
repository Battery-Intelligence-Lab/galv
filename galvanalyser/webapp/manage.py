from flask.cli import FlaskGroup
import click
import galvanalyserapp.database as database
import psycopg2
from app import app, config

cli = FlaskGroup(app)

@cli.command("create_db")
@click.confirmation_option(
    prompt='This will delete the current database, are you sure?'
)
def create_db():
    database.create_database(config)

@cli.command("create_user")
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_user(username, password):
    database.create_user(config, username, password)


if __name__ == "__main__":
    cli()
