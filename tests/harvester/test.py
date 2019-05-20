import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from timeit import default_timer as timer
import galvanalyser.harvester.input_file as input_file


start = timer()
f1 = input_file.InputFile("/Users/luke/Downloads/TPG1.2+-+Cell+15.002.xls")
end = timer()
print("f1 time")
print(end - start)
start = timer()
f2 = input_file.InputFile("/Users/luke/Downloads/TPG1+-+2+-+Cell+15+-+002.csv")
end = timer()
print("f2 time")
print(end - start)
start = timer()
f3 = input_file.InputFile("/Users/luke/Downloads/TPG1+-+2+-+Cell+15+-+002.txt")
end = timer()
print("f3 time")
print(end - start)

print(f1.get_column_to_standard_column_mapping(None))
print(f2.get_column_to_standard_column_mapping(None))
print(f3.get_column_to_standard_column_mapping(None))

start = timer()
print(f1.get_desired_data(None).keys())
end = timer()
print("f1 time")
print(end - start)
start = timer()
print(f2.get_desired_data(None).keys())
end = timer()
print("f2 time")
print(end - start)
start = timer()
print(f3.get_desired_data(None).keys())
end = timer()
print("f3 time")
print(end - start)
