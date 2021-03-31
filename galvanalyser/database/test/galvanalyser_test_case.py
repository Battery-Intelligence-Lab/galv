import unittest
import psycopg2
from pygalvanalyser.experiment.institution_row import InstitutionRow
import os


class GalvanalyserTestCase(unittest.TestCase):
    USER = 'test'
    USER_PWD = 'test'
    HARVESTER = 'my_test_harvester'
    HARVESTER_PWD = 'my_test_harvester'
    DATABASE = "gtest"
    INSTITUTION = "Oxford"

    @classmethod
    def setUpClass(self):
        self.user_conn = psycopg2.connect(
            host="galvanalyser_postgres",
            port=5433,
            database=self.DATABASE,
            user=self.USER,
            password=self.USER_PWD,
        )

        self.harvester_conn = psycopg2.connect(
            host="galvanalyser_postgres",
            port=5433,
            database=self.DATABASE,
            user=self.HARVESTER,
            password=self.HARVESTER_PWD,
        )
        self.oxford = InstitutionRow.select_from_name(
            self.INSTITUTION, self.harvester_conn
        )

    @classmethod
    def tearDownClass(self):
        self.user_conn.close()
        self.harvester_conn.close()
