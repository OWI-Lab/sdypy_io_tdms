SDyPy TDMS io
-----------------------

Basic package to import National Instruments .tdms files in a way complient with
SDyPy format for timeseries as proposed in SEP005.

Using the package
------------------

    .. code-block:: python

        from sdypy_io_tdms import read_tdms

        file_path = # Path to the tdms file of interest
        signals = read_tdms(file_path)
