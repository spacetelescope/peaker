Peaker
======

.. image:: https://github.com/spacetelescope/peaker/actions/workflows/tests.yml/badge.svg
    :target: https://codecov.io/gh/spacetelescope/peaker
    :alt: Coverage Status

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge


This package is designed to provide a PDF report of a calibration pipeline's regression
tests that keep track of the memory peaks, and help set the programming goals for
future builds. The PDF contains plots and a table with all said tests. The package
requires user credentials to Artifactory, and, for now, it works for JWST and ROMAN.



Installation
------------

Install with ```pip install peaker```.


Inputs
------

The code requires only one input, a text file with the Artifactory user credentials.
This file should only contain two variables with their corresponding values as
shown below:

`ART_USERNAME = username`

`ART_API_KEY = api_key_here`


Usage
-----

Run `peaker` from the terminal as:

.. code-block:: bash

    peaker somewhere/user_credentials.txt -p=2025-10-01to2026-03-26



Optional arguments
------------------

``--xmldir or -x``
    Path of the directory to save/read the XML files. If this flag is given, the
    Artifactory search will be skipped, e.g. -x=path/to/xml_files.

``--mission or -m``
    Name of the mission to analyze, i.e. -m=roman. Default is jwst.

``--days or -d``
    Number of days to show, e.g. -d=5 will show today and the last 4 days back. Default is None.

``--period or -p``
    Period of time to show. Input should be start to end, in the format year-month-day,
    local time, e.g. -p=2026-01-23to2026-02-27. Default is download everything up to today.

``--timezone or -t``
    Timezone to convert UTC time from xml files in the plots and report, e.g. -t=GMT. Default is EST.
    The code takes all IANA time zone strings. You can get a complete list of available
    timezones in your system with this in a python environment:

     .. code-block:: bash

        import zoneinfo
        print(zoneinfo.available_timezones())

``--version or -v``
    Python version tested in the regression tests, e.g. -v=3.11. Default is 3.12. Regression
    Tests will usually test at least 3 versions of Python.


Outputs
-------

There are a few outputs of the program:

1. A directory called `xmls` will be created in the same path as where the
   program is run. All the files downloaded from Artifactory will be there.

2. A directory called `peaker_outputs` will be created at the same level
   as the `xmls` directory. A `csv` file will be created in `peaker_outputs`.
   This file contains all the data obtained from the `xml` files that were
   successful pipeline runs.

3. A directory called `plots` will be created in the `peaker_outputs` directory.
   This directory contains a plot per regression test name. The test names
   are unique since it is a combination of the test name and the instrument
   mode tested. The instrument mode is obtained from the `class` the test
   belongs to. Each plot has two subplots, one of the peak memory versus
   dates (local time) and another for runtimes versus dates (local time).

4. A PDF report of the all regression tests that track memory peak and run
   times during the desired period of time. The report contains all the
   plots created as well as a summary of the `csv` table. The PDF table has
   the following columns: all unique test names, the instrument mode, the
   latest memory peak, the number of data points during that period, the
   difference of the median at the end of the period minus the median at
   the start of the period, and the page number in the PDF where the plot
   for that test can be found. This table is ordered from largest to
   lowest median differences, hence, a positive value indicates a memory
   increases at the end of the period with respect to the start, and a
   negative number indicates to an improvement at the end of the period
   with respect to the start of the period. When there are more than 5
   data points for a test, the start and end medians are calculated from
   the first 3 and last 3 memory peaks, respectively. If there are less
   than 5 data points, the difference is calculated from the last minus
   the first memory peak.



License
-------

See `LICENSE.rst` for more information.


Contributing
------------

We love contributions! `peaker` is open source,
built on open source, and we'd love to have you hang out in our community.
