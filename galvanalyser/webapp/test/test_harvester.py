from gtestcase import GTestCase
from timeit import default_timer as timer
import galvanalyser.harvester.input_file as input_file
import os

DATA_DIR = '/home/mrobins/git/tmp/galvanalyser_raw_datafiles'

class TestHarvester(GTestCase):
    def _test_upload_single(self, filename):
        start = timer()
        f = input_file.InputFile(filename)
        end = timer()
        print(f.get_column_to_standard_column_mapping(None))
        start = timer()
        print(f.get_desired_data(None).keys())
        end = timer()
        print("f time")
        print(end - start)


    def test_upload(self):
        for root, dirs, files in os.walk(DATA_DIR):
            for name in files:
                self._test_upload_single(os.path.join(root, name))
