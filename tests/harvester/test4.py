import os
import sys
from timeit import default_timer as timer
import statistics

columns = [
    "Cyc#",
    "Step",
    "StepTime",
    "Amp-hr",
    "Watt-hr",
    "Amps",
    "Volts",
    "State",
    "DPt Time",
]
data_size = 10000000

results = {}
print("Datasize: " + str(data_size))
print("-" * 80)
num_loops = 20
for loop in range(1, num_loops + 1):
    loop_start = timer()
    print("Loop " + str(loop) + " of " + str(num_loops))
    the_map = {
        column: [x * 1.5 for x in range(data_size)] for column in columns
    }

    start = timer()

    with open("/dev/null", "w") as f:
        for i in range(data_size):
            f.write(
                "\t".join([str(the_map[column][i]) for column in columns])
                + "\n"
            )

    end = timer()
    test_name = "map and index time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    map_iterators = [iter(the_map[column]) for column in columns]

    start = timer()

    with open("/dev/null", "w") as f:
        for i in range(data_size):
            f.write(
                "\t".join([str(next(iter_)) for iter_ in map_iterators]) + "\n"
            )

    end = timer()
    test_name = "map and iterator time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    the_map = None

    the_array = [[x * 1.5 for x in range(data_size)] for column in columns]

    start = timer()

    with open("/dev/null", "w") as f:
        for i in range(data_size):
            f.write("\t".join([str(column[i]) for column in the_array]) + "\n")

    end = timer()
    test_name = "array and index time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    class DataRowGenerator:
        def __init__(self, data):
            self.data = data

        def get_data_row_generator(self):
            iterators = [iter(column) for column in self.data]
            while True:
                yield "\t".join(
                    [str(next(iterator)) for iterator in iterators]
                )

    dg = DataRowGenerator(the_array)

    start = timer()
    with open("/dev/null", "w") as f:
        f.writelines(dg.get_data_row_generator())
    end = timer()
    test_name = "generator and iterators time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    start = timer()
    with open("/dev/null", "w") as f:
        for line in dg.get_data_row_generator():
            f.write(line + "\n")
    end = timer()
    test_name = "generator and iterators write time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    class DataRowGenerator2:
        def __init__(self, data):
            self.data = data

        def get_data_row_generator(self):
            iterators = [iter(column) for column in self.data]
            for i in range(len(self.data[0])):
                yield "\t".join(
                    [str(next(iterator)) for iterator in iterators]
                )

    dg2 = DataRowGenerator2(the_array)
    start = timer()
    with open("/dev/null", "w") as f:
        f.writelines(dg2.get_data_row_generator())
    end = timer()
    test_name = "generator and iterators 2 time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    start = timer()
    with open("/dev/null", "w") as f:
        f.writelines(("\t".join(map(str, x)) for x in zip(*the_array)))
    end = timer()
    test_name = "zip time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    start = timer()
    with open("/dev/null", "w") as f:
        for elems in zip(*the_array):
            f.write("\t".join(map(str, elems)))
    end = timer()
    test_name = "zip write time"
    results[test_name] = results.get(test_name, []) + [end - start]
    print("{}: {:.2f}".format(test_name, end - start))

    print("Finished loop " + str(loop) + " of " + str(num_loops))

    def min_sorter(kvp):
        return min(kvp[1])

    for key, values in sorted(results.items(), key=min_sorter):
        print(
            "\t{}: min ( {:.2f} ) median ( {:.2f} ) mean ( {:.2f} ) max ( {:.2f} )".format(
                key,
                min(values),
                statistics.median(values),
                statistics.mean(values),
                max(values),
            )
        )
    loop_stop = timer()
    loop_time = loop_stop - loop_start
    remaining_loops = num_loops - (loop)
    print(
        "Loop took {:.2f} seconds, {} loops remain expected time {:.2f}".format(
            loop_time, remaining_loops, remaining_loops * loop_time
        )
    )
    print("-" * 80)


# Finished loop 200 of 200
#        zip write time: min ( 32.12 ) median ( 33.44 ) mean ( 33.40 ) max ( 35.74 )
#        zip time: min ( 32.35 ) median ( 33.06 ) mean ( 33.14 ) max ( 35.83 )
#        array and index time: min ( 38.05 ) median ( 40.16 ) mean ( 40.14 ) max ( 42.36 )
#        map and iterator time: min ( 40.01 ) median ( 42.79 ) mean ( 42.70 ) max ( 46.69 )
#        map and index time: min ( 40.16 ) median ( 42.40 ) mean ( 42.31 ) max ( 44.05 )
#        generator and iterators time: min ( 40.28 ) median ( 41.06 ) mean ( 41.24 ) max ( 43.95 )
#        generator and iterators 2 time: min ( 40.41 ) median ( 41.70 ) mean ( 41.71 ) max ( 43.57 )
#        generator and iterators write time: min ( 41.14 ) median ( 42.68 ) mean ( 42.68 ) max ( 44.11 )
# Loop took 335.48 seconds, 0 loops remain expected time 0.00
