# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import io
import sys


class IteratorFile(io.TextIOBase):
    """ given an iterator which yields strings,
    return a file like object for reading those strings """

    def __init__(self, it):
        self._it = it
        self._f = io.StringIO()
        self.buffered_chars = 0

    def read(self, length=sys.maxsize):

        try:
            while self.buffered_chars < length:
                self.buffered_chars += self._f.write(next(self._it) + "\n")

        except StopIteration as e:
            # soak up StopIteration. this block is not necessary because
            # of finally, but just to be explicit
            pass

        except:  # Exception as e:
            raise
        #            print("uncaught exception: {}".format(e))

        finally:
            self._f.seek(0)
            data = self._f.read(length)

            # save the remainder for next read
            remainder = self._f.read()
            self._f.seek(0)
            self._f.truncate(0)
            self.buffered_chars = self._f.write(remainder)
            return data

    def readline(self):
        try:
            # load up a line to make sure that there is one to read
            self._f.write(next(self._it) + "\n")
        except StopIteration as e:
            # soak up StopIteration. this block is not necessary because
            # of finally, but just to be explicit
            pass

        except:  # Exception as e:
            raise
        #            print("uncaught exception: {}".format(e))

        finally:
            self._f.seek(0)
            data = self._f.readline()

            # save the remainder for next read
            remainder = self._f.read()
            self._f.seek(0)
            self._f.truncate(0)
            # store size of data in buffer for the read method
            self.buffered_chars = self._f.write(remainder)
            return data
