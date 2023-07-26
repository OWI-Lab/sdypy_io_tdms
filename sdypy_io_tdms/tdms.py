import os
import warnings

import numpy as np
from nptdms import TdmsFile


def read_tdms(path):
    """Primary function to read tdms files based on the path.

    .. code-block:: python
        signals = dw.readTDMS(path, location)

    Returns an empty list when file failed

    :param path: path to a .tdms file
    """

    if not os.path.isfile(path):
        warnings.warn("FAILED IMPORT: No TDMS file at: " + path, UserWarning)
        signals = []
        return signals

    try:
        tdms_file = TdmsFile(path)
    except FileNotFoundError as fnf_error:
        warnings.warn(
            f"FAILED IMPORT: No TDMS file at: {path}",
            UserWarning
        )
        signals = []
        return signals
    except ValueError as val_error:
        warnings.warn(
            f"FAILED IMPORT: TDMS file at: {path} seems corrupted. Failed to import.",
            UserWarning
        )
        signals = []
        return signals

    signals = []
    groups = tdms_file.groups()

    for group in groups:
        channels = tdms_file[group.name].channels()
        for channel in channels:
            signal = {}
            signal['group'] = group
            signal['name'] = str(channel).split("/")[2][1:-2]
            if "unit_string" in channel.properties:
                unit_str = channel.properties["unit_string"]
            else:
                unit_str = ""
            signal['unit_str'] = unit_str
            signal['data'] = tdms_file[group.name][channel.name].data
            signal['fs'] = 1 / channel.properties["wf_increment"]
            signal['start_timestamp'] = np.datetime_as_string(channel.properties["wf_start_time"], unit='s')
            signals.append(signal)

    return signals