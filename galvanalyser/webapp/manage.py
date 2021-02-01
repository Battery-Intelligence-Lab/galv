from flask.cli import FlaskGroup
import click
import psycopg2
from app import app, config
import copy
import unittest
import os
import sys
import galvanalyserapp.redash as redash
import galvanalyserapp.database as database

cli = FlaskGroup(app)

@cli.command("test")
def test():
    import test.gtestcase as gtestcase

    test_config = copy.copy(config)
    test_config["db_conf"]["database_name"] = gtestcase.test_database
    database.create_database(test_config)

    # run webapp tests
    test_suite = unittest.defaultTestLoader.discover('test/')
    runner = unittest.TextTestRunner()
    runner.run(test_suite)


@cli.command("test_harvester")
@click.option('--path', default='/usr/src/app/galvanalyser/harvester/test')
def test(path):
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
    database.create_database(test_config)

    database.create_user(
        test_config,
        HarvesterTestCase.USER,
        HarvesterTestCase.USER_PWD
    )
    database.create_institution(
        test_config,
        HarvesterTestCase.HARVESTER_INSTITUTION
    )
    database.create_harvester(
        test_config,
        HarvesterTestCase.HARVESTER_ID,
        HarvesterTestCase.HARVESTER_PWD
    )

    database.add_harvester_path(
        test_config,
        HarvesterTestCase.HARVESTER_ID,
        HarvesterTestCase.DATA_DIR,
        [HarvesterTestCase.USER],
    )

    # run harvester tests
    test_suite = unittest.defaultTestLoader.discover(path)
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


if __name__ == "__main__":
    cli()
