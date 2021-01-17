import psycopg2
import os

def create_database(config):
    print('Creating database....')
    _create(config)
    print('Applying initial migrations....')
    _setup(config)
    print('Finished creating database.')


def _database_exists(cur):
    cur.execute("SELECT datname FROM pg_database;")
    return ('galvanalyser',) in cur.fetchall()


def _create(config):
    conn = psycopg2.connect(
            host=config["db_conf"]["database_host"],
            port=config["db_conf"]["database_port"],
            database="postgres",
            user=config["db_conf"]["database_user"],
            password=config["db_conf"]["database_pwd"],
        )

    conn.autocommit = True
    with conn.cursor() as cur:
        if _database_exists(cur):
            print('in create():"galvanalyser" database already exists, dropping')
            cur.execute("DROP DATABASE galvanalyser;")
        filename = os.path.join(
            os.path.dirname(__file__),
            "create-database.pgsql"
        )
        cur.execute(open(filename, "r").read())

    conn.close()


def _setup(config):
    conn = psycopg2.connect(
            host=config["db_conf"]["database_host"],
            port=config["db_conf"]["database_port"],
            database="galvanalyser",
            user=config["db_conf"]["database_user"],
            password=config["db_conf"]["database_pwd"],
        )

    with conn.cursor() as cur:
        # drop roles if they exist
        cur.execute("SELECT rolname FROM pg_roles;")
        roles = cur.fetchall()
        if ('normal_user',) in roles:
            cur.execute("DROP ROLE normal_user;")
        if ('harvester',) in roles:
            cur.execute("DROP ROLE harvester;")
        conn.commit()
        filename = os.path.join(
            os.path.dirname(__file__),
            "setup.pgsql"
        )
        cur.execute(open(filename, "r").read())

    conn.commit()
    conn.close()

