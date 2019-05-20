import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

import galvanalyser.harvester.maccor_functions as maccor_functions
import xlrd

maccor_functions.load_metadata_maccor_excel(
    "/Users/luke/Downloads/TPG1.2+-+Cell+15.002.xls"
)


class LogFilter(object):
    def write(self, *args):
        if len(args) != 1 or not (
            args[0] == "\n"
            or args[0]
            == "WARNING *** OLE2 inconsistency: SSCS size is 0 but SSAT size is non-zero"
        ):
            print("".join(args))

    def writelines(self, *args):
        pass

    def close(self, *args):
        pass


file_path = "/Users/luke/Downloads/TPG1.2+-+Cell+15.002.xls"
with xlrd.open_workbook(
    file_path, on_demand=True, logfile=LogFilter()
) as wbook:
    sheet = wbook.sheet_by_index(0)
    for i in range(0, sheet.ncols):
        print(str(i) + ': "' + str(sheet.cell_value(0, i)) + '"')
        print(sheet.cell_value(0, i))
