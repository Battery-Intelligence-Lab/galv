from flask.cli import FlaskGroup

from app import app

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    print('creating db')


if __name__ == "__main__":
    cli()
