import copy
import datetime
import os
import warnings
from pathlib import Path
from typing import Union

import numpy as np
from nptdms import TdmsFile, ChannelObject, GroupObject, RootObject, TdmsWriter
from sdypy_sep005.sep005 import assert_sep005


def read_tdms(path: Union[str, Path]) -> list:
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
    except FileNotFoundError:
        warnings.warn(
            f"FAILED IMPORT: No TDMS file at: {path}",
            UserWarning
        )
        signals = []
        return signals
    except ValueError:
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
            signal = {
                'group': group.name,
                'name': str(channel).split("/")[2][1:-2]
            }
            if "unit_string" in channel.properties:
                unit_str = channel.properties["unit_string"]
            else:
                unit_str = ""
            signal['unit_str'] = unit_str
            signal['data'] = tdms_file[group.name][channel.name].data
            signal['fs'] = 1 / channel.properties["wf_increment"]
            if 'wf_start_time' in channel.properties:
                signal['start_timestamp'] = np.datetime_as_string(
                    channel.properties["wf_start_time"],
                    unit='s'
                )
            signals.append(signal)

    return signals


def write_tdms(
        signals: Union[list, dict],
        path: Union[str, Path],
        author: str = 'sdypy_io_tdms',
        timestamp=None
):
    """Write a SEP005 formatted object into a TDMS file
    """
    if not isinstance(signals, (list, tuple)):
        signals = [signals]  # Convert single instance to a list

    if timestamp is None:
        for signal in signals:
            if 'start_timestamp' in signal:
                if isinstance(signal['start_timestamp'], datetime.datetime):
                    timestamp = copy.copy(signal['start_timestamp'])
                    signal['start_timestamp'] = str(signal['start_timestamp'])

        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

    # Check if SEP005 compliant
    assert_sep005(signals)

    root_object = RootObject(
        properties={
            "author": author,
            "datestring": timestamp.strftime("%Y/%m/%d H:%M:%S"),
        }
    )

    with TdmsWriter(path, "w") as tdms_writer:
        tdms_writer.write_segment([root_object])
        for signal in signals:
            if signal['group'] is None:
                raise ValueError(
                    "signal.group attribute should not be None as it is required for a TDMS file"
                )
            group_object = GroupObject(signal['group'])
            channel_object = ChannelObject(
                signal['group'],
                signal['name'],
                np.array(signal['data'], dtype="float32"),
                properties={
                    "unit_string": signal['unit_str'],
                    "wf_increment": 1 / signal['fs'],
                },
            )
            tdms_writer.write_segment([group_object, channel_object])
