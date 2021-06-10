from flask.cli import FlaskGroup
import click
import psycopg2
from app import app
import copy
import unittest
import os
import sys
from galvanalyserapp.redash import CustomRedash
import galvanalyserapp.database as database
from pygalvanalyser.harvester.monitored_path_row import MonitoredPathRow
from harvester.__main__ import main as harvester_main
import json
import subprocess

cli = FlaskGroup(app)


@cli.command("test_api")
@click.option('--path', default='/usr/src/app/galvanalyser/database/test')
def test_api(path):
    if not os.path.exists(os.path.join(path, 'galvanalyser_test_case.py')):
        raise RuntimeError((
            'galvanalyser_test_case.py does not exist in {}. '
            'Is the path correct?').format(path)
        )

    sys.path.append(path)
    from galvanalyser_test_case import GalvanalyserTestCase

    test_config = copy.copy(app.config)
    test_config["db_conf"]["database_name"] = GalvanalyserTestCase.DATABASE

    # create database environment that test case expects
    database.create_database(
        test_config,
        test=True
    )

    database.create_user(
        test_config,
        GalvanalyserTestCase.USER,
        GalvanalyserTestCase.USER_PWD,
        test=True
    )
    database.create_institution(
        test_config,
        GalvanalyserTestCase.INSTITUTION
    )

    # run harvester tests
    test_suite = unittest.defaultTestLoader.discover(path)
    runner = unittest.TextTestRunner()
    runner.run(test_suite)


@cli.command("test_harvester")
@click.option('--path', default='/usr/src/app/galvanalyser/harvester/test')
@click.option('--test', default='')
def test(path, test):
    if not os.path.exists(os.path.join(path, 'harvester_test_case.py')):
        raise RuntimeError((
            'harvester_test_case.py does not exist in {}. '
            'Is the path correct?').format(path)
        )

    sys.path.append(path)
    from harvester_test_case import HarvesterTestCase

    test_config = copy.copy(app.config)
    test_config["GALVANISER_DATABASE"]["NAME"] = HarvesterTestCase.DATABASE

    # create database environment that harvester test case expects
    database.create_database(
        test_config,
        test=True
    )

    database.create_user(
        test_config,
        HarvesterTestCase.USER,
        HarvesterTestCase.USER_PWD,
        test=True
    )
    database.create_institution(
        test_config,
        HarvesterTestCase.HARVESTER_INSTITUTION
    )

    database.create_harvester_user(
        test_config,
        HarvesterTestCase.HARVESTER,
        HarvesterTestCase.HARVESTER_PWD,
        test=True
    )
    database.create_machine_id(
        test_config,
        HarvesterTestCase.MACHINE_ID,
    )

    database.add_machine_path(
        test_config,
        HarvesterTestCase.MACHINE_ID,
        HarvesterTestCase.DATA_DIR,
        [HarvesterTestCase.USER],
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
def create_user(username, password):
    database.create_user(app.config, username, password)


@cli.command("create_institution")
@click.option('--name', prompt=True)
def create_institution(name):
    database.create_institution(app.config, name)


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
def create_machine_id(machine_id):
    database.create_machine_id(app.config, machine_id)


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


@cli.command("print_queries")
@click.option('--api_key', prompt=True)
def print_queries(api_key):
    redash = CustomRedash('http://server:5000', api_key)
    saved_queries = []
    for query in redash.paginate(redash.queries):
        q = redash.query(query['id'])
        for v in q['visualizations']:
            v.pop('created_at')
            v.pop('updated_at')
        saved_query = {
            k: q[k] for k in ['id', 'name', 'options', 'query', 'visualizations']
        }
        saved_queries.append(saved_query)
    print(json.dumps(saved_queries, indent=2))


@cli.command("print_dashboards")
@click.option('--api_key', prompt=True)
def print_dashboards(api_key):
    redash = CustomRedash('http://server:5000', api_key)
    saved_dashboards = []
    for dashboard in redash.paginate(redash.dashboards):
        d = redash.dashboard(dashboard['slug'])
        saved_dashboards.append(d)
    print(json.dumps(saved_dashboards, indent=2))


if __name__ == "__main__":
    cli()
