import psycopg2
import os

def database_exists(cur):
    cur.execute("SELECT datname FROM pg_database;")
    return ('galvanalyser',) in cur.fetchall()

def create(conn):
    conn.autocommit = True
    with conn.cursor() as cur:
        if database_exists(cur):
            print('in create():"galvanalyser" database already exists, dropping')
            cur.execute("DROP DATABASE galvanalyser;")
        filename = os.path.join(
            os.path.dirname(__file__),
            "create-database.pgsql"
        )
        cur.execute(open(filename, "r").read())

def setup(conn):
    with conn.cursor() as cur:
        if database_exists(cur):
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
        else:
            print('in setup(): "galvanalyser" database does not exist')

