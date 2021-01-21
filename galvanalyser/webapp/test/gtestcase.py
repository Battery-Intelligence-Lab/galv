import unittest
import psycopg2

test_database = "gtest"

class GTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.conn = psycopg2.connect(
            host="postgres",
            port=5432,
            database=test_database,
            user="postgres",
            password=os.getenv('POSTGRES_PASSWORD'),
        )

    @classmethod
    def tearDownClass(self):
        self.conn.close()
