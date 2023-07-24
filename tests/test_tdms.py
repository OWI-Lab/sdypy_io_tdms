import pytest

from sdypy_io_tdms.tdms import read_tdms



def test_import_faulty_tdms():
    """
    Test the import of a faulty tdms, should return a UserWarning and an empty signal list

    :return:
    """
    import os.path

    TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'static', 'faulty_tdms_01.tdms')
    with pytest.warns(UserWarning):
        signals = read_tdms(TESTDATA_FILENAME)

    assert signals == []

def test_no_file_on_path():
    """
    Test that a UserWarning is returned when an incorrect path is provided, and an empty signal list is returned
    :return:
    """
    with pytest.warns(UserWarning):
        signals = read_tdms('dummy.tdms')

    assert signals == []