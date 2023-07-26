import os

import pytest
from sdypy_sep005.sep005 import assert_sep005

from sdypy_io_tdms.tdms import read_tdms

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')
# With respect to project root (where pytest is run)
GOOD_TDMS_FILES = os.listdir(os.path.join(static_dir, 'good'))
BAD_TDMS_FILES = os.listdir(os.path.join(static_dir, 'bad'))


@pytest.mark.parametrize("filename", GOOD_TDMS_FILES)
def test_content(filename):
    TEST_FILE_PROP = {
        'good_tdms_1.tdms': {
            'no_channels': 8,
            'total_sum': -15.59784792,  # Sum of all values inside the channels
            'length': 18000,
            'unit_str': 'g',
            'fs': 30,
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
        }
    }
    file_path = os.path.join(static_dir, 'good', filename)
    signals = read_tdms(file_path)
    assert len(signals) != 0  # Not an empty response
    assert len(signals) == TEST_FILE_PROP[filename]['no_channels']

    tot_sum = 0
    for s, s_name in zip(signals, TEST_FILE_PROP[filename]['channel_names']):
        assert s['name'] == s_name
        assert s['unit_str'] == TEST_FILE_PROP[filename]['unit_str']
        assert len(s['data']) == TEST_FILE_PROP[filename]['length']
        assert s['fs'] == pytest.approx(TEST_FILE_PROP[filename]['fs'])
        tot_sum += sum(s['data'])

    # Total sum of the data should match between the original file and the imported
    assert tot_sum == pytest.approx(TEST_FILE_PROP[filename]['total_sum'])


@pytest.mark.parametrize("filename", GOOD_TDMS_FILES)
def test_compliance_sep005(filename):
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
    import os.path

    file_path = os.path.join(static_dir, 'bad', filename)
    with pytest.warns(UserWarning, match=filename):
        signals = read_tdms(file_path)

    assert signals == []


def test_no_file_on_path():
    """
    Test that a UserWarning is returned when an incorrect path is provided, and an empty signal list is returned
    :return:
    """
    with pytest.warns(UserWarning):
        signals = read_tdms('dummy.tdms')

    assert signals == []