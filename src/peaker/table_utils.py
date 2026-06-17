"""Utilities to create a csv file with all data obtained per test."""

import os
import numpy as np
from astropy.table import Table
from collections import OrderedDict

from .utils import convert_units


def _mk_table_content(tests_ran):
    table_content = {}
    for test_name, test_dict in tests_ran.items():
        # make sure the lists are sorted per date (oldest will be first in the list)
        table_content[test_name] = {}
        arr_size = len(test_dict["date"])
        if arr_size > 1:
            sorted_idx = np.argsort(test_dict["date"])
            test_dict["date"] = sorted(test_dict["date"])
            #test_dict["time"] = [test_dict["time"][i] for i in sorted_idx]  -> not used at this time
            test_dict["peakmem"] = np.array(test_dict["peakmem"])[sorted_idx]
            bytes_peakmem = test_dict["peakmem"]

            # Calculate the number of points to be considered in beginning and end medians
            if arr_size in [2, 3, 4]:
                # stats for the first start_stats dates of period
                start_median = np.median(bytes_peakmem[0])
                start_mean = np.mean(bytes_peakmem[0])
                start_std = np.std(bytes_peakmem[0])
                # stats for last 3 days of period
                end_median = np.median(bytes_peakmem[1])
                end_mean = np.mean(bytes_peakmem[1])
                end_std = np.std(bytes_peakmem[1])
            elif arr_size >= 5:
                start_stats = 3
                end_stats = start_stats - 1
                # stats for the first start_stats dates of period
                start_median = np.median(bytes_peakmem[:start_stats])
                start_mean = np.mean(bytes_peakmem[:start_stats])
                start_std = np.std(bytes_peakmem[:start_stats])
                # stats for last 3 days of period
                end_median = np.median(bytes_peakmem[-end_stats:])
                end_mean = np.mean(bytes_peakmem[-end_stats:])
                end_std = np.std(bytes_peakmem[-end_stats:])
        else:
            bytes_peakmem = test_dict["peakmem"][0]
            start_median = bytes_peakmem
            start_mean = bytes_peakmem
            start_std = bytes_peakmem
            end_median = bytes_peakmem
            end_mean = bytes_peakmem
            end_std = bytes_peakmem

        peakmem, units = convert_units(bytes_peakmem)
        if arr_size == 1:
            latest_date = test_dict["date"]
            latest_peakmem = np.round(peakmem, decimals=3)
            second_to_last = np.nan
        else:
            latest_date = test_dict["date"][-1]
            latest_peakmem = float(np.round(peakmem[-1], decimals=3))
            second_to_last = float(np.round(peakmem[-2], decimals=3))

        table_content[test_name] = {
            "test_class": test_dict["classname"],
            "latest_date": latest_date,
            "units": units,
            "latest_peakmem": latest_peakmem,
            "second_to_last": second_to_last,
            "data_points": arr_size,
            # stats for the whole period
            "tot_median": np.median(bytes_peakmem),
            "tot_mean": np.mean(bytes_peakmem),
            "tot_std": np.std(bytes_peakmem),
            "start_median": start_median,
            "start_mean": start_mean,
            "start_std": start_std,
            "end_median": end_median,
            "end_mean": end_mean,
            "end_std": end_std,
            # difference from start and end
            "diff_median": end_median - start_median,
            "diff_mean": end_mean - start_mean,
            "diff_std": np.sqrt((start_std*start_std + end_std*end_std)/2),
        }
    # Now make sure the dictionary is ordered by difference of start and end medians
    ordered_table_content = OrderedDict(sorted(table_content.items(), 
                                               key=lambda item: item[1]["diff_median"], reverse=True))
    # convert units from bytes to MB or other unit as needed
    for test_name, test_dict in ordered_table_content.items():
        for key, value in test_dict.items():
            if "mean" in key or "std" in key or "median" in key:
                value, _ = convert_units(value, desired_units=test_dict["units"])
                ordered_table_content[test_name][key] = np.round(value, decimals=3)
    return ordered_table_content


def _get_instrument_mode(table_content, pools):
    inst_mode = []
    for test_name in table_content.keys():
        tn_mode = test_name.split(sep="_M_")
        tn = tn_mode[0].replace("test_", "")
        mode = tn_mode[1]
        if pools:
            if "pool" in tn and tn in pools:
                mode = pools[tn]
        inst_mode.append(mode)
    return inst_mode


def generate_report_table(output, mission, pools=None, show_table=False):
    """
    Generates an astropy Table and prints it in a csv file.

    Parameters
    ----------
    output : class
        A dataclass with the following elements:
        outdir - Full path for the output directory.
        tests_ran - Dictionary will have the test name are the keys and a subdictionary
            containing an array of dates, peak memory, and corresponding run times.
        local_sdate - Start date (Local time) for files with data.
        local_edate - End date (Local time) for files with data.
        report_table - Table of test data organized by test name and class.
        plots - List of plots.
    mission : str
        Mission name.
    pools : dict
        Dictionary of pool names and their respective meanings.
    show_table : bool
        Print on-screen the table as well as the csv file.
    """
    # Create the table content
    table_content = _mk_table_content(output.tests_ran)

    # Define the report table
    rt = Table()

    # Set the table title
    table_title = "Regression_Tests_Memory_Peaks_from_{}_to_{}".format(output.local_sdate, output.local_edate)
    rt.meta["name"] = table_title

    # Fill in the table using the dictionary of all tests ran
    rt["Test_name"] = [test_name.replace("test_", "").split(sep="_M_")[0] for test_name in table_content.keys()]
    rt["Instrument_mode"] = _get_instrument_mode(table_content, pools)
    if pools:
        rt["Class"] = [test_name.replace("test_", "").split(sep="_M_")[1] for test_name in table_content.keys()]
    rt["Units"] = [test_dict["units"] for _, test_dict in table_content.items()]
    rt["Latest_peakmem"] = [test_dict["latest_peakmem"] for _, test_dict in table_content.items()]
    rt["Data_points"] = [test_dict["data_points"] for _, test_dict in table_content.items()]
    rt["Diff_medians"] = [test_dict["diff_median"] for _, test_dict in table_content.items()]
    rt["Diff_means"] = [test_dict["diff_mean"] for _, test_dict in table_content.items()]
    rt["Diff_stddevs"] = [test_dict["diff_std"] for _, test_dict in table_content.items()]
    rt["Median_tot"] = [test_dict["tot_median"] for _, test_dict in table_content.items()]
    rt["Mean_tot"] = [test_dict["tot_mean"] for _, test_dict in table_content.items()]
    rt["Std_dev_tot"] = [test_dict["tot_std"] for _, test_dict in table_content.items()]
    rt["Median_start"] = [test_dict["start_median"] for _, test_dict in table_content.items()]
    rt["Mean_start"] = [test_dict["start_mean"] for _, test_dict in table_content.items()]
    rt["Std_dev_start"] = [test_dict["start_std"] for _, test_dict in table_content.items()]
    rt["Median_end"] = [test_dict["end_median"] for _, test_dict in table_content.items()]
    rt["Mean_end"] = [test_dict["end_mean"] for _, test_dict in table_content.items()]
    rt["Std_dev_end"] = [test_dict["end_std"] for _, test_dict in table_content.items()]
    output.report_table = rt

    if show_table:
        print(rt)

    csv_file = mission.upper() + "_" + table_title+".csv"
    csv_file = str(output.outdir / csv_file)
    rt.write(csv_file, format="csv", overwrite=True)
    print(" Table saved: ", os.path.abspath(csv_file))
