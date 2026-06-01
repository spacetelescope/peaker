"""Fixtures for tests."""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from astropy.table import Table

from peaker.parse_xmls import Output


@pytest.fixture(scope="session")
def tmpdir(tmp_path_factory):
    return tmp_path_factory.mktemp("tmpdir")


@pytest.fixture(scope="session")
def expected_output():
    tests_ran = {
        'test_std[pool_006_spec_nirspec_FIXED_SLIT_AND_jw00217]_M_associations_sdp_pools': {
            'date': [datetime(2026, 2, 9, 19, 7, 45, 258429,
                                       tzinfo=ZoneInfo(key='America/New_York')),
                     datetime(2026, 2, 13, 19, 7, 45, 258429,
                                       tzinfo=ZoneInfo(key='America/New_York'))],
            'peakmem': [6600170, 6600170], 'time': [10.427935403999982, 10.427935403999982],
            'test_name': 'test_std[pool_006_spec_nirspec_FIXED_SLIT_AND_jw00217]_M_associations_sdp_pools',
            'classname': 'jwst.regtest.associations_sdp_pools.test_associations_sdp_pools'
        },
        'test_std[pool_004_wfs]_M_associations_sdp_pools': {
            'date': [datetime(2026, 2, 9, 19, 7, 45, 258429,
                                       tzinfo=ZoneInfo(key='America/New_York')),
                     datetime(2026, 2, 13, 19, 7, 45, 258429,
                                       tzinfo=ZoneInfo(key='America/New_York'))],
            'peakmem': [9691991, 9691991], 'time': [42.4346264589999, 42.4346264589999],
            'test_name': 'test_std[pool_004_wfs]_M_associations_sdp_pools',
            'classname': 'jwst.regtest.associations_sdp_pools.test_associations_sdp_pools'
        },
        'test_log_tracked_resources_spec2[jw02072-o002_20221206t143745_spec2_00001_asn.json]_M_nirspec_fs_spec2': {
            'date': [datetime(2026, 2, 9, 19, 7, 45, 258429,
                                       tzinfo=ZoneInfo(key='America/New_York')),
                      datetime(2026, 2, 13, 19, 7, 45, 258429,
                                        tzinfo=ZoneInfo(key='America/New_York'))],
            'peakmem': [1081170864, 1081170864], 'time': [183.64004175799982, 183.64004175799982],
            'test_name': 'test_log_tracked_resources_spec2[jw02072-o002_20221206t143745_spec2_00001_asn.json]_M_nirspec_fs_spec2',
            'classname': 'jwst.regtest.test_nirspec_fs_spec2'},
        'test_pool_miri_wfss_M_associations_sdp_pools_slow_jw09505': {
         'date': [datetime(2026, 2, 9, 19, 7, 45, 258429, tzinfo=ZoneInfo(key='America/New_York')),
                  datetime(2026, 2, 13, 19, 7, 45, 258429, tzinfo=ZoneInfo(key='America/New_York'))],
         'peakmem': [4262560, 4262560], 'time': [3.931779634999657, 3.931779634999657],
         'test_name': 'test_pool_miri_wfss_M_associations_sdp_pools_slow_jw09505',
         'classname': 'jwst.regtest.associations_sdp_pools.test_associations_sdp_pools_slow_jw09505'
        },
        'test_jw04237_20250321t192812_dms_pool_M_associations_sdp_pools_slow_jw04237_2': {
         'date': [datetime(2026, 2, 9, 19, 7, 45, 258429,
                                    tzinfo=ZoneInfo(key='America/New_York')),
                  datetime(2026, 2, 13, 19, 7, 45, 258429,
                                    tzinfo=ZoneInfo(key='America/New_York'))],
         'peakmem': [157210699, 157210699], 'time': [1025.570868151999, 1025.570868151999],
         'test_name': 'test_jw04237_20250321t192812_dms_pool_M_associations_sdp_pools_slow_jw04237_2',
         'classname': 'jwst.regtest.associations_sdp_pools.test_associations_sdp_pools_slow_jw04237_2'
        }
    }

    plots = [
        "test_std[pool_006_spec_nirspec_FIXED_SLIT_AND_jw00217]_M_associations_sdp_pools.png",
        "test_std[pool_004_wfs]_M_associations_sdp_pools.png",
        "test_log_tracked_resources_spec2[jw02072-o002_20221206t143745_spec2_00001_asn.json]_M_nirspec_fs_spec2.png",
        "test_pool_miri_wfss_M_associations_sdp_pools_slow_jw09505.png",
        "test_jw04237_20250321t192812_dms_pool_M_associations_sdp_pools_slow_jw04237_2.png"
    ]

    date_format = "%Y-%m-%d"
    expected_oldest_date = datetime.strptime("2026-02-09", date_format)
    expected_latest_date = datetime.strptime("2026-02-13", date_format)
    expected_local_sdate = expected_oldest_date.astimezone().date()
    expected_local_edate = expected_latest_date.astimezone().date()

    rt = Table()
    table_title = "Regression_Tests_Memory_Peaks_from_{}_to_{}".format(expected_local_sdate, expected_local_edate)
    rt.meta["name"] = table_title
    rt["Test_name"] = ["std[pool_006_spec_nirspec_FIXED_SLIT_AND_jw00217]",
                       "std[pool_004_wfs]",
                       "log_tracked_resources_spec2[jw02072-o002_20221206t143745_spec2_00001_asn.json]",
                       "pool_miri_wfss",
                       "jw04237_20250321t192812_dms_pool"]
    rt["Instrument_mode"] = ["associations_sdp_pools",
                             "associations_sdp_pools",
                             "nirspec_fs_spec2",
                             "associations_sdp_pools_slow_jw09505",
                             "associations_sdp_pools_slow_jw04237_2"]
    rt["Units"] = ["MB", "MB", "GB", "MB", "MB"]
    rt["Latest_peakmem"] = [6.294, 9.243, 1.007, 4.065, 149.928]
    rt["Data_points"] = [2, 2, 2, 2, 2]
    rt["Diff_medians"] = [0.0, 0.0, 0.0, 0.0, 0.0]
    rt["Diff_means"] = [0.0, 0.0, 0.0, 0.0, 0.0]
    rt["Diff_stddevs"] = [0.0, 0.0, 0.0, 0.0, 0.0]
    rt["Median_tot"] = [6.294, 9.243, 1.007, 4.065, 149.928]
    rt["Mean_tot"] = [6.294, 9.243, 1.007, 4.065, 149.928]
    rt["Std_dev_tot"] = [0.0, 0.0, 0.0, 0.0, 0.0]
    rt["Median_start"] = [6.294, 9.243, 1.007, 4.065, 149.928]
    rt["Mean_start"] = [6.294, 9.243, 1.007, 4.065, 149.928]
    rt["Std_dev_start"] = [0.0, 0.0, 0.0, 0.0, 0.0]
    rt["Median_end"] = [6.294, 9.243, 1.007, 4.065, 149.928]
    rt["Mean_end"] = [6.294, 9.243, 1.007, 4.065, 149.928]
    rt["Std_dev_end"] = [0.0, 0.0, 0.0, 0.0, 0.0]

    output = Output(Path.cwd(), tests_ran, expected_local_sdate, expected_local_edate, rt, plots)
    return output
