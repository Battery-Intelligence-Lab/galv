from timeit import default_timer as timer
import input_file


start = timer()
f1 = input_file.InputFile('/Users/luke/Downloads/TPG1+-+2+-+Cell+15+-+002-2.csv')
end = timer()
print('f1 time')
print(end - start)

print(f1.get_column_to_standard_column_mapping())
# print(f2.get_column_to_standard_column_mapping(None))
# print(f3.get_column_to_standard_column_mapping(None))

start = timer()
data = f1.get_standardized_data({'Rec#':'Rec#'})
end = timer()
print('f1.get_standardized_data time')
print(end - start)
start = timer()
f1.write_output_file('/tmp/outputfile.csv', data)
end = timer()
print('f1.write_output_file time')
print(end - start)
# start = timer()
# print(f3.get_desired_data(None).keys())
# end = timer()
# print('f3 time')
# print(end - start)