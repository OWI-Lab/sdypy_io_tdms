SDyPy TDMS io
-----------------------

Basic package to import National Instruments `.tdms` files in a way compliant with
SDyPy format for timeseries as proposed in SEP005.

Using the package
------------------

    .. code-block:: python

        from sdypy_io_tdms import read_tdms

        file_path = # Path to the tdms file of interest
        signals = read_tdms(file_path)

Acknowledgements
----------------
This package was developed in the framework of the [Interreg Smart Circular Bridge project](https://vb.nweurope.eu/projects/project-search/smart-circular-bridge-scb-for-pedestrians-and-cyclists-in-a-circular-built-environment/)
