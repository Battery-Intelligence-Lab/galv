import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)


from timeit import default_timer as timer
import galvanalyser.harvester.input_file as input_file


def do_test(path, test_no):
    start = timer()
    f = input_file.InputFile(path)
    end = timer()
    print("f{} time".format(test_no))
    print(end - start)
    start = timer()
    data = f.get_data_row_generator(["sample_no", "volts", "amps", "power"])
    end = timer()
    print("f{}.get_standardized_data time".format(test_no))
    print(end - start)
    start = timer()
    with open("/tmp/test3_{}.txt".format(test_no), "w") as f:
        f.writelines((line + "\n" for line in data))
    end = timer()
    print("f{}.write_output_file time".format(test_no))
    print(end - start)


files = [
    "/Users/luke/Downloads/TPG1+-+2+-+Cell+15+-+002-2.csv",
    "/Users/luke/Downloads/TPG1.2+-+Cell+15.002.xls",
    "/Users/luke/code/battery-project/harvester-test/test-data/Ivium_Cell+1.txt",
]

for test_no, path in enumerate(files):
    do_test(path, test_no)
