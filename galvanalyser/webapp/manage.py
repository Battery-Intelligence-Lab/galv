from flask.cli import FlaskGroup
import click
import psycopg2
from app import app, config
import copy
import unittest
import os
import sys
from galvanalyserapp.redash import CustomRedash
import galvanalyserapp.database as database
import json

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

    test_config = copy.copy(config)
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

    test_config = copy.copy(config)
    test_config["db_conf"]["database_name"] = HarvesterTestCase.DATABASE

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

@cli.command("create_db")
@click.confirmation_option(
    prompt='This will delete the current database, are you sure?'
)
def create_db():
    database.create_database(config)

@cli.command("create_user")
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_user(username, password):
    database.create_user(config, username, password)


@cli.command("create_institution")
@click.option('--name', prompt=True)
def create_institution(name):
    database.create_institution(config, name)


@cli.command("create_harvester")
@click.option('--harvester', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_harvester(harvester, password):
    database.create_harvester_user(config, harvester, password)


@cli.command("create_machine_id")
@click.option('--machine_id', prompt=True)
def create_machine_id(machine_id):
    database.create_machine_id(config, machine_id)


@cli.command("add_machine_path")
@click.option('--machine_id', prompt=True)
@click.option('--path', prompt=True)
@click.option('--user', multiple=True, prompt=True)
def add_machine_path(machine_id, path, user):
    database.add_machine_path(config, machine_id, path, user)


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
