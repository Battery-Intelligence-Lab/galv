import unittest
import psycopg2
from galvanalyser import init_database
import os

import flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class GalvanalyserTestCase(unittest.TestCase):
    USER = 'test'
    USER_PWD = 'test'
    HARVESTER = 'my_test_harvester'
    HARVESTER_PWD = 'my_test_harvester'
    DATABASE = "gtest"
    DATA_DIR = '/usr/test_data'
    MACHINE_ID = 'my_test_harvester'
    POSTGRES_USER = 'postgres'
    POSTGRES_USER_PWD = os.getenv('POSTGRES_PASSWORD')

    @classmethod
    def setUpClass(self):
        app = flask.Flask(__name__)

        app.config.from_mapping(
            {
                'SQLALCHEMY_DATABASE_URI':
                    'postgresql://{}:{}@{}/{}'.format(
                        self.POSTGRES_USER,
                        self.POSTGRES_USER_PWD,
                        'galvanalyser_postgres:5433',
                        self.DATABASE,
                    ),
                'SQLALCHEMY_ECHO': True,
                'SQLCHEMY_TRACK_MODIFICATIONS': False,
                'SQLALCHEMY_BINDS': {
                    'harvester': 'postgresql://{}:{}@{}/{}'.format(
                        self.HARVESTER,
                        self.HARVESTER_PWD,
                        'galvanalyser_postgres:5433',
                        self.DATABASE,
                    ),
                    },
            }
        )
        print(app.config)

        self.Session, self.HarvesterSession = init_database(app.config)

        self.harvester_conn = psycopg2.connect(
            host="galvanalyser_postgres",
            port=5433,
            database=self.DATABASE,
            user=self.HARVESTER,
            password=self.HARVESTER_PWD,
        )

        self.postgres_conn = psycopg2.connect(
            host="galvanalyser_postgres",
            port=5433,
            database=self.DATABASE,
            user=self.POSTGRES_USER,
            password=self.POSTGRES_USER_PWD,
        )

    @classmethod
    def tearDownClass(self):
        self.harvester_conn.close()
        self.postgres_conn.close()
