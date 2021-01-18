import psycopg2
from psycopg2 import sql
import os
from pygalvanalyser.harvester.harvester_row import HarvesterRow
from pygalvanalyser.harvester.monitored_path_row import MonitoredPathRow
from pygalvanalyser.experiment.institution_row import InstitutionRow

def create_user(config, username, password):
    conn = _create_superuser_connection(config)
    _create_user(conn, username, password, is_harvester=False)
    conn.close()


def create_institution(config, name):
    conn = _create_superuser_connection(config)
    institution = InstitutionRow.select_from_name(name, conn)
    if institution is None:
        InstitutionRow(name=name).insert(conn)

    conn.commit()


def create_harvester(config, machine_id, password):
    conn = _create_superuser_connection(config)

    # create harvester user
    _create_user(conn, machine_id, password, is_harvester=True)

    # if machine_id does not already exist then create it
    harvester = HarvesterRow.select_from_machine_id(machine_id, conn)
    if harvester is None:
        HarvesterRow(machine_id).insert(conn)

    conn.commit()
    conn.close()


def add_harvester_path(config, machine_id, path, users):
    conn = _create_superuser_connection(config)

    harvester = HarvesterRow.select_from_machine_id(machine_id, conn)
    if harvester is None:
        raise RuntimeError(
            'machine_id "{}" does not exist'.format(machine_id)
        )

    MonitoredPathRow(
        harvester.id,
        '{' + ','.join(users) + '}',
        path
    ).insert(conn)

    conn.commit()
    conn.close()


def create_database(config, name):
    print('Creating database....')
    _create(config, name)
    print('Applying initial migrations....')
    _setup(config, name)
    print('Finished creating database.')


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


def _database_exists(cur, name):
    cur.execute("SELECT datname FROM pg_database;")
    return (name,) in cur.fetchall()


def _create_superuser_connection(config):
    return psycopg2.connect(
        host=config["db_conf"]["database_host"],
        port=config["db_conf"]["database_port"],
        database=config["db_conf"]["database_name"],
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
    db_name = config["db_conf"]["database_name"]
    with conn.cursor() as cur:
        if _database_exists(cur, db_name):
            print(
                'in create():"{}" database already exists, dropping'.format(db_name)
            )
            cur.execute(sql.SQL("DROP DATABASE {db_name};").format(db_name=db_name))

        cur.execute(sql.SQL("""
            CREATE DATABASE {db_name}
                WITH
                OWNER = postgres
                ENCODING = 'UTF8'
                LC_COLLATE = 'en_US.utf8'
                LC_CTYPE = 'en_US.utf8'
                TABLESPACE = pg_default
                CONNECTION LIMIT = -1;
                """).format(db_name=db_name))

    conn.close()


def _setup(config, name):
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

        # set timezone
        cur.execute(
            sql.SQL(
                "ALTER DATABASE {db_name} SET timezone TO 'UTC';"
            ).format(db_name=config["db_conf"]["database_name"])
        )

        cur.execute("SELECT pg_reload_conf();")

        # create initial database
        filename = os.path.join(
            os.path.dirname(__file__),
            "setup.pgsql"
        )
        cur.execute(open(filename, "r").read())

    conn.commit()
    conn.close()

