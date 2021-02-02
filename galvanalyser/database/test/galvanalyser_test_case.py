import unittest
import psycopg2
import os


class GalvanalyserTestCase(unittest.TestCase):
    USER = 'test'
    USER_PWD = 'test'
    DATABASE = "gtest"
    INSTITUTION = "Oxford"

    @classmethod
    def setUpClass(self):
        self.conn = psycopg2.connect(
            host="galvanalyser_postgres",
            port=5433,
            database=self.DATABASE,
            user=self.USER,
            password=self.USER_PWD,
        )

    @classmethod
    def tearDownClass(self):
        self.conn.close()
