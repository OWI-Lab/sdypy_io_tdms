import datetime
import os

import numpy as np
import pytest
from pytz import utc
from sdypy_sep005.sep005 import assert_sep005

from sdypy_io_tdms.tdms import read_tdms, write_tdms

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')
# With respect to project root (where pytest is run)
GOOD_TDMS_FILES = os.listdir(os.path.join(static_dir, 'good'))
BAD_TDMS_FILES = os.listdir(os.path.join(static_dir, 'bad'))


@pytest.mark.parametrize("filename", GOOD_TDMS_FILES)
def test_content(filename):
    """
    Use test files to assert the correct data is being loaded from the tdms file
    """
    test_file_prop = {
        'good_tdms_1.tdms': {
            'no_channels': 8,
            'total_sum': -15.59784792,  # Sum of all values inside the channels
            'length': [18000] * 8,
            'group': ['acceleration'] * 8,
            'unit_str': ['g'] * 8,
            'fs': [30] * 8,
            'channel_names': [
                'TP_ACC_LAT19_315deg_X',
                'TP_ACC_LAT19_315deg_Y',
                'TW_ACC_LAT27_031deg_X',
                'TW_ACC_LAT27_031deg_Y',
                'TW_ACC_LAT41_031deg_X',
                'TW_ACC_LAT41_031deg_Y',
                'TW_ACC_LAT69_031deg_X',
                'TW_ACC_LAT69_031deg_Y'
            ]
        },
        'good_tdms_2.tdms': {
            'no_channels': 24,
            'total_sum': 41137.14263 + 227876.64,  # Sum of all values inside the channels
            'length': [15000] * 8 + [1] + [60] * 6 + [1] * 2 + [4] * 7,
            'group': ['acceleration'] * 8 + ['ambient'] * 16,
            'unit_str': ['g'] * 8 + ['C'] + ['Â°'] * 3 + ['m/s'] * 3 +
                        ['hPa'] + ['%', 'mm', 'hits', 'sec', 'sec', 'hits/H', 'hits/H', 'V'],
            'fs': [250] * 8 + [1 / 60] + [1] * 6 + [1 / 60] * 2 + [1 / 15] * 7,
            'channel_names': [
                'SCB_ALM_RS_ACC_HOR004_X_nr1',
                'SCB_ALM_RS_ACC_HOR004_Z_nr3',
                'SCB_ALM_RS_ACC_HOR008_X_nr1',
                'SCB_ALM_RS_ACC_HOR008_Y_nr2',
                'SCB_ALM_RS_ACC_HOR008_Z_nr3',
                'SCB_ALM_RS_ACC_HOR012_X_nr1',
                'SCB_ALM_RN_ACC_HOR012_Y_nr2',
                'SCB_ALM_RN_ACC_HOR012_Z_nr3',
                'temperature air',
                'displacement min',
                'displacement avg',
                'displacement max',
                'wind speed min',
                'wind speed avg',
                'wind speed max',
                'pressure',
                'humidity',
                'precepitation rain',
                'precepitation hail',
                'duration rain',
                'duration hail',
                'intensity rain',
                'intensity hail',
                'voltage supply'
            ]
        }
    }
    file_path = os.path.join(static_dir, 'good', filename)
    signals = read_tdms(file_path)
    assert len(signals) != 0  # Not an empty response
    assert len(signals) == test_file_prop[filename]['no_channels']

    tot_sum = 0
    for signal, s_name, s_unit_str, s_len, s_fs, s_g in zip(
            signals,
            test_file_prop[filename]['channel_names'],
            test_file_prop[filename]['unit_str'],
            test_file_prop[filename]['length'],
            test_file_prop[filename]['fs'],
            test_file_prop[filename]['group']
    ):
        assert signal['name'] == s_name
        assert signal['group'] == s_g
        assert signal['unit_str'] == s_unit_str
        assert len(signal['data']) == s_len
        assert signal['fs'] == pytest.approx(s_fs)
        tot_sum += np.sum(signal['data'], dtype=np.float64)

    # Total sum of the data should match between the original file and the imported
    assert tot_sum == pytest.approx(test_file_prop[filename]['total_sum'])


@pytest.mark.parametrize("filename", GOOD_TDMS_FILES)
def test_compliance_sep005(filename):
    """
    Test the compliance with the SEP005 guidelines
    """
    file_path = os.path.join(static_dir, 'good', filename)
    signals = read_tdms(file_path)  # should already not crash here

    assert len(signals) != 0  # Not an empty response
    assert_sep005(signals)


@pytest.mark.parametrize("filename", BAD_TDMS_FILES)
def test_import_faulty_tdms(filename):
    """
    Test the import of a faulty tdms, should return a UserWarning and an empty signal list

    :return:
    """

    file_path = os.path.join(static_dir, 'bad', filename)
    with pytest.warns(UserWarning, match=filename):
        signals = read_tdms(file_path)

    assert not signals


def test_no_file_on_path():
    """
    Test that a UserWarning is returned when an incorrect path is provided,
     and an empty signal list is returned
    :return:
    """
    with pytest.warns(UserWarning):
        signals = read_tdms('dummy.tdms')

    assert not signals


def test_write_tdms(tmp_path):
    """
    Test that checks to write a tdms file from a SEP005 compliant structure and then reads it again
    """
    signals = [
        {
            'name': 'test_01',
            'group': 'acceleration',
            'unit_str': 'm/s²',
            'data': np.array([1, 2, 3, 4, 5, 4.12, 3, 2, 1]),
            'fs': 2.50,
            'start_timestamp': datetime.datetime(2023, 11, 15, 12, tzinfo=utc)
        },
        {
            'name': 'test_02',
            'group': 'strain',
            'unit_str': 'microstrain',
            'data': np.array([1, 2, 3, 4, 5.23, 4, 3, 2, 1]),
            'fs': 1.0,
            'start_timestamp': datetime.datetime(2023, 11, 15, 12, tzinfo=utc)
        }
    ]
    temp_dir = tmp_path / 'write_tdms'
    temp_dir.mkdir()
    tdms_path = temp_dir / "write_test.tdms"
    write_tdms(signals, tdms_path)
    assert os.path.isfile(tdms_path)  # A file was created

    signals_read = read_tdms(tdms_path)
    assert len(signals_read) == len(signals)
    for signal_r, signal in zip(signals_read, signals):
        assert signal_r['name'] == signal['name']
        assert signal_r['fs'] == signal['fs']
        assert signal_r['unit_str'] == signal['unit_str']
        assert signal_r['group'] == signal['group']
        assert np.allclose(signal_r['data'], signal['data'])

    # Check it can also handle just a single instance
    tdms_path = temp_dir / "write_test_single.tdms"
    write_tdms(signals[0], tdms_path)
    assert os.path.isfile(tdms_path)  # A file was created
    signals_read = read_tdms(tdms_path)
    assert len(signals_read) == 1
