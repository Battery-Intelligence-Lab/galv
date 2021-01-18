import psycopg2
from psycopg2 import sql
import os


def create_user(config, username, password):
    conn = _create_superuser_connection(config)
    with conn.cursor() as cur:
        # drop user if they exist
        user_ident = sql.Identifier(username)
        cur.execute(
            sql.SQL("DROP USER IF EXISTS {user}").format(user=user_ident)
        )
        # create user
        cur.execute(sql.SQL(
            """
            CREATE USER {user} WITH
              LOGIN
              NOSUPERUSER
              INHERIT
              NOCREATEDB
              NOCREATEROLE
              NOREPLICATION
              PASSWORD %(passwd)s;
            GRANT normal_user TO {user};
            """
        ).format(user=user_ident), {'passwd': password})
    conn.commit()

def create_database(config):
    print('Creating database....')
    _create(config)
    print('Applying initial migrations....')
    _setup(config)
    print('Finished creating database.')


def _database_exists(cur):
    cur.execute("SELECT datname FROM pg_database;")
    return ('galvanalyser',) in cur.fetchall()

def _create_superuser_connection(config):
    return psycopg2.connect(
        host=config["db_conf"]["database_host"],
        port=config["db_conf"]["database_port"],
        database="galvanalyser",
        user=config["db_conf"]["database_user"],
        password=config["db_conf"]["database_pwd"],
    )

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
    conn = _create_superuser_connection(config)

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

