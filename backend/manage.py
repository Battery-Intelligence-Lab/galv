from flask.cli import FlaskGroup
import click
import psycopg2
from app import app
import copy
import unittest
import os
import sys
from galvanalyser import Session
import galvanalyser.database as database
from galvanalyser.database.harvester import MonitoredPathRow
from galvanalyser.harvester.harvester import main as harvester_main
from galvanalyser.database.user_data import UserRow, Group, User
from sqlalchemy import select
import json
import subprocess

cli = FlaskGroup(app)

@cli.command("test")
@click.option('--path', default='/usr/app/test')
@click.option('--test', default='')
def test(path, test):
    if not os.path.exists(os.path.join(path, 'galvanalyser_test_case.py')):
        raise RuntimeError((
            'galvanalyser_test_case.py does not exist in {}. '
            'Is the path correct?').format(path)
        )

    sys.path.append(path)
    from galvanalyser_test_case import GalvanalyserTestCase

    test_config = copy.copy(app.config)
    test_config["GALVANISER_DATABASE"]["NAME"] = GalvanalyserTestCase.DATABASE

    # create database environment that test case expects
    database.create_database(
        test_config,
        test=True
    )

    # create test user
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    user = UserRow(
        GalvanalyserTestCase.USER,
        password=GalvanalyserTestCase.USER_PWD,
        email='test@gmail.com'
    )
    user.insert(conn)
    conn.commit()

    database.create_harvester_user(
        test_config,
        GalvanalyserTestCase.HARVESTER,
        GalvanalyserTestCase.HARVESTER_PWD,
        test=True
    )

    database.create_machine_id(
        test_config,
        GalvanalyserTestCase.MACHINE_ID,
        GalvanalyserTestCase.HARVESTER,
    )

    database.add_machine_path(
        test_config,
        GalvanalyserTestCase.MACHINE_ID,
        GalvanalyserTestCase.DATA_DIR,
        [user.id],
    )

    # run harvester tests
    if test == '':
        test_suite = unittest.defaultTestLoader.discover(path)
    else:
        test_suite = unittest.defaultTestLoader.loadTestsFromName(test)

    runner = unittest.TextTestRunner()
    runner.run(test_suite)


@cli.command("create_galvanalyser_db")
@click.confirmation_option(
    prompt='This will delete the current database, are you sure?'
)
def create_galvanalyser_db():
    database.create_database(app.config)
    database.create_harvester_user(
        app.config,
        os.getenv('HARVESTER_USERNAME'),
        os.getenv('HARVESTER_PASSWORD')
    )

@cli.command("create_redash_db")
@click.confirmation_option(
    prompt='This will delete the current database, are you sure?'
)
def create_redash_db():
    backup_file = 'galvanalyserapp/database/redash_backup.sql'
    try:
        process = subprocess.Popen(
            ['pg_restore',
             '--clean',
             '--if-exists',
             '--dbname={}'
             .format(app.config['db_conf']['redash_url']),
             backup_file],
            stdout=subprocess.PIPE
        )
        output = process.communicate()[0]
        if int(process.returncode) != 0:
            print('Command failed. Return code : {}'
                  .format(process.returncode))
        return output
    except Exception as e:
        print("Issue with the db restore : {}".format(e))


@cli.command("backup_redash_db")
def backup_redash_db():
    backup_file = '/usr/data/redash_backup.sql'
    try:
        process = subprocess.Popen(
            ['pg_dump',
             '--dbname={}'
             .format(app.config['db_conf']['redash_url']),
             '-Fc',
             '-f', backup_file],
            stdout=subprocess.PIPE
        )
        output = process.communicate()[0]
        if int(process.returncode) != 0:
            print('Command failed. Return code : {}'
                  .format(process.returncode))
            exit(1)
        return output
    except Exception as e:
        print(e)
        exit(1)


@cli.command("create_user")
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--email', prompt=True)
@click.option('--admin/--no-admin', prompt=True)
def create_user(username, password, email, admin):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    UserRow.create(username, password, email).insert(conn)
    conn.commit()
    if admin:
        with Session() as session:
            # TODO: change above UserRow to a User to reuse here
            user = session.execute(
                select(User).where(User.username == username)
            ).scalar_one()
            admin = session.execute(
                select(Group).where(Group.groupname == 'admin')
            ).scalar_one()
            user.groups.append(admin)
            session.commit()


@cli.command("create_harvester")
@click.option('--harvester', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_harvester(harvester, password):
    if harvester == 'harvester':
        print('ERROR: "{}" is not a valid harvester name'.format(harvester))
        return
    database.create_harvester_user(app.config, harvester, password)


@cli.command("create_machine_id")
@click.option('--machine_id', prompt=True)
@click.option('--harvester_name', prompt=True)
def create_machine_id(machine_id, harvester_name):
    database.create_machine_id(
        app.config, machine_id, harvester_main
    )


@cli.command("add_machine_path")
@click.option('--machine_id', prompt=True)
@click.option('--path', prompt=True)
@click.option('--user', prompt=True)
def add_machine_path(machine_id, path, user):
    if os.path.isabs(path):
        print(
            'Please enter a relative path to GALVANALYSER_HARVESTER_BASE_PATH'
        )
        return

    database.add_machine_path(app.config, machine_id, path, [user])


@cli.command("edit_machine_path")
@click.option('--machine_id', prompt=True)
def edit_machine_path(machine_id):
    database.edit_machine_path(app.config, machine_id)


@cli.command("run_harvester")
@click.option('--harvester', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--machine_id', prompt=True)
def run_harvester(harvester, password, machine_id):
    harvester_main(
        harvester, password, machine_id,
        'galvanalyser_postgres', '5433',
        'galvanalyser', base_path='/usr/data'
    )

if __name__ == "__main__":
    cli()
