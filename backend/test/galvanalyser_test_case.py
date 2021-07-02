import unittest
import psycopg2
from galvanalyser.database.experiment import InstitutionRow
import os


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
