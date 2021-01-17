from flask.cli import FlaskGroup
import galvanalyserapp.database as database
import psycopg2
from app import app, config

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    conn = psycopg2.connect(
            host=config["db_conf"]["database_host"],
            port=config["db_conf"]["database_port"],
            database="postgres",
            user=config["db_conf"]["database_user"],
            password=config["db_conf"]["database_pwd"],
        )
    database.create(conn)
    conn.close()

    conn = psycopg2.connect(
            host=config["db_conf"]["database_host"],
            port=config["db_conf"]["database_port"],
            database="galvanalyser",
            user=config["db_conf"]["database_user"],
            password=config["db_conf"]["database_pwd"],
        )
    database.setup(conn)
    conn.commit()
    conn.close()
    print('finished create_db')


if __name__ == "__main__":
    cli()
