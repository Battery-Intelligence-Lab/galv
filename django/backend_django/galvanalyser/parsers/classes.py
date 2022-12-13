import pathlib
from typing import List


class FileParseError(BaseException):
    pass


class Parser:
    """
    A Parser presents information from a dataset in a standardized format.
    That format breaks data down into default columns and non-default columns.
    Data are presented using Parser.read() which yields a row of data as key-value pairs.
    Metadata can be accessed via the Parser.metadata object.
    These are not guaranteed to conform to any particular structure.
    """
    extensions: List[str] = []
    default_columns = []
    raw_data = None
    metadata = {}
    ready: bool = False

    def __init__(self, path: pathlib.Path = None, default_columns=None):
        if default_columns is not None:
            self.default_columns = [{'id': c.id, 'name': c.name} for c in default_columns]
        self.path = path

    def read(self):
        """
        Return a row of key-value pairs binding column names to cell values.
        """
        return {}
