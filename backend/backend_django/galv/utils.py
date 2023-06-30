# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import os
import re

from .models import MonitoredPath, Harvester, ObservedFile


def get_monitored_paths(path: os.PathLike|str, harvester: Harvester) -> list[MonitoredPath]:
    """
    Return the MonitoredPaths on this Harvester that match the given path.
    MonitoredPaths are matched by path and regex.
    """
    monitored_paths = MonitoredPath.objects.filter(harvester=harvester)
    monitored_paths = [p for p in monitored_paths if os.path.abspath(path).startswith(os.path.abspath(p.path))]
    return [p for p in monitored_paths if re.search(p.regex, os.path.relpath(path, p.path))]


# TODO: If these lookups are too slow, we could keep track of the monitored_path used
# each time a file is reported on, and use that to lookup files by path directly.
def get_files_from_path(path: MonitoredPath) -> list[ObservedFile]:
    """
    Return a list of files from the given path that match the MonitoredPath's regex.
    """
    files = ObservedFile.objects.filter(path__startswith=path.path, harvester=path.harvester)
    if not path.regex:
        out = files
    else:
        regex = re.compile(path.regex)
        out = [p for p in files if re.search(regex, os.path.relpath(p.path, path.path))]
    return out
