import psycopg2
from psycopg2 import sql
import os

def create_user(config, username, password):
    conn = _create_superuser_connection(config)
    _create_user(conn, username, password, is_harvester=False)
    conn.close()

def _create_user(conn, username, password, is_harvester=False):
    with conn.cursor() as cur:
        # drop user if they exist
        user_ident = sql.Identifier(username)
        cur.execute(
            sql.SQL("DROP USER IF EXISTS {user}").format(user=user_ident)
        )
        # create user
        user_type = 'normal_user'
        if is_harvester:
            user_type = 'harvester'
        user_type = sql.Identifier(user_type)
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
            GRANT {type} TO {user};
            """
        ).format(user=user_ident, type=user_type),
                    {'passwd': password})
    conn.commit()

def create_institution(config, name):
    conn = _create_superuser_connection(config)
    with conn.cursor() as cur:
        # don't do anything if institution already exists
        cur.execute("SELECT name FROM experiment.institution;")
        if (name,) not in cur.fetchall():
            cur.execute(
                "INSERT INTO experiment.institution (name) VALUES (%s);",
                [name]
            )
    conn.commit()

def _create_harvester_machine(conn, name):
    with conn.cursor() as cur:
        # don't do anything if machine already exists
        cur.execute("SELECT name FROM experiment.institution;")
        if (name,) not in cur.fetchall():
            cur.execute(
                "INSERT INTO experiment.institution (name) VALUES (%s);",
                [name]
            )
    conn.commit()


def create_harvester(config, machine_id, password):
    conn = _create_superuser_connection(config)

    # create harvester user
    _create_user(conn, machine_id, password, is_harvester=True)

    # if machine_id does not already exist then create it
    with conn.cursor() as cur:
        cur.execute("SELECT (machine_id) FROM harvesters.harvester;")
        machine_ids = cur.fetchall()
        if (machine_id,) not in machine_ids:
            # create harvester machine
            cur.execute(
                "INSERT INTO harvesters.harvester (machine_id) VALUES (%s);",
                [machine_id]
            )
    conn.commit()
    conn.close()


def add_harvester_path(config, machine_id, path, users):
    conn = _create_superuser_connection(config)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM harvesters.harvester WHERE machine_id=%s;",
            [machine_id]
        )
        response = cur.fetchone()
        if response is None:
            raise RuntimeError(
                'machine_id "{}" does not exist'.format(machine_id)
            )
        harvester_id = response[0]

        cur.execute(
            (
                "INSERT INTO harvesters.monitored_path "
                "(harvester_id, path, monitored_for) "
                "VALUES (%s, %s, %s);"
            ),
            [harvester_id, path, '{' + ','.join(users) + '}']
        )

    conn.commit()
    conn.close()



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

