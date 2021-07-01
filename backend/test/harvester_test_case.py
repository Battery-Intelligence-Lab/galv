import unittest
import psycopg2
import os


class HarvesterTestCase(unittest.TestCase):
    DATA_DIR = '/usr/test_data'
    USER = 'test'
    USER_PWD = 'test'
    HARVESTER = 'my_test_harvester'
    MACHINE_ID = 'my_test_harvester'
    HARVESTER_PWD = 'my_test_harvester'
    DATABASE = "gtest"
    HARVESTER_INSTITUTION = 'Oxford'

    @classmethod
    def setUpClass(self):
        self.conn = psycopg2.connect(
            host="galvanalyser_postgres",
            port=5433,
            database=self.DATABASE,
            user=self.HARVESTER,
            password=self.HARVESTER_PWD,
        )

    @classmethod
    def tearDownClass(self):
        self.conn.close()
