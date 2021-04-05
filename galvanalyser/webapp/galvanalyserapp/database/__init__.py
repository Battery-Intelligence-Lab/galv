import psycopg2
from psycopg2 import sql
import string
import os
from pygalvanalyser.harvester.harvester_row import HarvesterRow
from pygalvanalyser.harvester.monitored_path_row import MonitoredPathRow
from pygalvanalyser.experiment.institution_row import InstitutionRow

def create_user(config, username, password, test=False):
    conn = _create_superuser_connection(config)
    if test:
        role = 'test_user'
    else:
        role = 'normal_user'

    _create_user(conn, username, password, role)
    conn.close()

def create_harvester_user(config, harvester, password, test=False):
    conn = _create_superuser_connection(config)

    if test:
        role = 'test_harvester'
    else:
        role = 'harvester'

    # create harvester user
    _create_user(conn, harvester, password, role)

    conn.close()

def create_institution(config, name):
    conn = _create_superuser_connection(config)
    institution = InstitutionRow.select_from_name(name, conn)
    if institution is None:
        InstitutionRow(name=name).insert(conn)

    conn.commit()
    conn.close()


def create_machine_id(config, machine_id):
    conn = _create_superuser_connection(config)

    # if machine_id does not already exist then create it
    harvester = HarvesterRow.select_from_machine_id(machine_id, conn)
    if harvester is None:
        HarvesterRow(machine_id).insert(conn)

    conn.commit()
    conn.close()


def add_machine_path(config, machine_id, path, users):
    conn = _create_superuser_connection(config)

    harvester = HarvesterRow.select_from_machine_id(machine_id, conn)
    if harvester is None:
        raise RuntimeError(
            'machine_id "{}" does not exist'.format(machine_id)
        )

    format_users = '{' + ','.join(users) + '}'

    MonitoredPathRow(
        harvester.id,
        format_users,
        path
    ).insert(conn)

    conn.commit()
    conn.close()


def create_database(config, test=False):
    print('Creating database....')
    _create(config)
    print('Applying initial migrations....')
    _setup(config, test)
    print('Finished creating database.')


def _create_user(conn, username, password, role='normal_user'):
    with conn.cursor() as cur:
        # drop user if they exist
        user_ident = sql.Identifier(username)
        cur.execute(
            sql.SQL("DROP USER IF EXISTS {user}").format(user=user_ident)
        )
        # create user
        user_type = sql.Identifier(role)
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
            cur.execute(
                sql.SQL(
                    "DROP DATABASE {db_name};"
                ).format(db_name=sql.Identifier(db_name)))

        cur.execute(sql.SQL("""
            CREATE DATABASE {db_name}
                WITH
                OWNER = postgres
                ENCODING = 'UTF8'
                LC_COLLATE = 'en_US.utf8'
                LC_CTYPE = 'en_US.utf8'
                TABLESPACE = pg_default
                CONNECTION LIMIT = -1;
                """).format(db_name=sql.Identifier(db_name)))

    conn.close()


def _setup(config, test=False):
    conn = _create_superuser_connection(config)
    if test:
        user_role = 'test_user'
        harvester_role = 'test_harvester'
    else:
        user_role = 'normal_user'
        harvester_role = 'harvester'
    print('using roles', user_role, harvester_role)

    with conn.cursor() as cur:
        # create roles if they dont exist
        cur.execute("SELECT rolname FROM pg_roles;")
        roles = cur.fetchall()
        for role in [user_role, harvester_role]:
            if (role,) not in roles:
                cur.execute(sql.SQL("""
                    CREATE ROLE {role} WITH
                      NOLOGIN
                      NOSUPERUSER
                      INHERIT
                      NOCREATEDB
                      NOCREATEROLE
                      NOREPLICATION;
                """).format(role=sql.Identifier(role)))
        conn.commit()

        # set timezone
        cur.execute(
            sql.SQL(
                "ALTER DATABASE {db_name} SET timezone TO 'UTC';"
            ).format(
                db_name=sql.Identifier(
                    config["db_conf"]["database_name"]
                )
            )
        )

        cur.execute("SELECT pg_reload_conf();")

        # create initial database
        filename = os.path.join(
            os.path.dirname(__file__),
            "setup.pgsql"
        )
        cur.execute(
            string.Template(
                open(filename, "r").read()
            ).substitute(
                user_role=user_role,
                harvester_role=harvester_role,
            )
        )

    conn.commit()
    conn.close()

