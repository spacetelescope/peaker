"""Parses xml files."""

from glob import glob
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from xml.etree import ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


def _parse_single_xml(filename):
    # Create the Element Tree object from the xml file and get the top level, root
    tree = ET.parse(filename)
    root = tree.getroot()

    # Save all the info into the following dictionary and use a specific datetime format
    peakmem_dict = {}
    date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    # The first element is called testsuites, this only contains one testsuite, which
    # has the datetime in which the tests were ran, variable called timestamp, in UT.
    failures = 0
    for element in root.iter("testsuites"):
        items = element.findall("testsuite")[0]
        if items is not None:
            test_date = datetime.strptime(items.attrib["timestamp"], date_format)
            # Also get the failures variable
            failures = int(items.attrib["failures"])

    # Sanity check
    if not test_date:
        raise ValueError("No test date found in xml file.")

    # All test cases will be under the testsuite element.
    for element in root.iter("testcase"):
        # For this element, the peak memory is under properties/property
        tracked_mem_elements = element.findall("properties/property")

        # If this list does not exist, no memory peak was recorded
        if tracked_mem_elements:
            # some tests have the same name but are run for different modes
            # get the class and store it
            classname = element.attrib["classname"]
            # add the instrument mode to the test name from the class
            inst_mode = classname.split(sep="test_")[-1]
            # get the test name and make it unique
            test_name = element.attrib["name"] + "_M_" + inst_mode
            # make sure the test name does not contain / because this
            # causes problems with pathlib
            if "/" in test_name:
                test_name = test_name.replace("/", "--")
            peakmem_dict[test_name] = {}
            peakmem_dict[test_name]["classname"] = classname
            for prop in tracked_mem_elements:
                # save the peak memory and running time
                if prop.attrib["name"] == "tracked-peakmem":
                    peakmem_dict[test_name]["peakmem"] = prop.get("value")
                elif prop.attrib["name"] == "tracked-time":
                    peakmem_dict[test_name]["time"] = prop.get("value")

    return test_date, failures, peakmem_dict


@dataclass
class Output:
    """Structure containing output information."""
    outdir: Path
    tests_ran: dict
    local_sdate: None
    local_edate: None
    report_table: list
    plots: list


def parse_xmls(xmldir, localtz):
    """Parse all the XML files and store the data into a dictionary.

    Parameters
    ----------
    xmldir : pathlib.Path
        Full path for directory where to find the xml files.
    localtz : str
        Local timezone for peaker outputs.

    Returns
    -------
    output : class
        A dataclass with the following elements:
        outdir - Full path for the output directory.
        tests_ran - Dictionary will have the test name are the keys and a subdictionary
            containing an array of dates, peak memory, and corresponding run times.
        local_sdate - Start date (Local time) for files with data.
        local_edate - End date (Local time) for files with data.
        report_table - Table of test data organized by test name and class.
        plots - List of plots.

    """
    # Make a list of all files in output directory
    xml_files = [xmlfile for xmlfile in glob(str(xmldir) + "/*.xml")]
    
    print(" Parsing xml ", len(xml_files), " files ... ")
    if len(xml_files) == 0:
        print("\n * No xml files to parse. Exiting program.\n")
        exit()

    total_failures = 0
    file_without_data = 0
    successful_runs = 0
    tests_ran = {}
    oldest_date, latest_date = datetime.now(UTC).astimezone(), None
    for i, xmlfile in enumerate(xml_files):
        ut_test_date, failures, peakmem_dict = _parse_single_xml(xmlfile)

        # Convert timestamp from UTC to local time
        test_date = ut_test_date.astimezone(ZoneInfo(localtz))
        if test_date <= oldest_date:
            oldest_date = test_date

        # Define latest_date in first pass, then compare
        if i == 0:
            latest_date = test_date
        if test_date >= latest_date:
            latest_date = test_date

        if failures > 0:
            # Failed run, ignore this file
            total_failures += 1
            print("   Failed run: ", test_date, xmlfile)

        elif peakmem_dict:
            successful_runs += 1
            for test_name, test_dict in peakmem_dict.items():
                classname = test_dict["classname"]
                peakmem = int(test_dict["peakmem"])
                runtime = float(test_dict["time"])

                # Add data entry to test in dictionary for existing test and class
                if test_name in tests_ran:
                    tests_ran[test_name]["date"].append(test_date)
                    tests_ran[test_name]["peakmem"].append(peakmem)
                    tests_ran[test_name]["time"].append(runtime)

                # Create a dictionary entry if the test is not in there
                else:
                    tests_ran[test_name] = {
                        "date": [test_date],
                        "peakmem": [peakmem],
                        "time": [runtime],
                        "test_name": test_name,
                        "classname": classname,
                    }
        else:
            print("   File without tests data: ", test_date, xmlfile)
            file_without_data += 1
    print(" Files ignored due to failures: ", total_failures)
    print(" Files without tests data: ", file_without_data)
    print(" Successful runs: ", successful_runs)

    for test_name in tests_ran:
        print("   Data points for {}: {}".format(test_name, len(tests_ran[test_name]["date"])))

    # Create an output directory
    outdir = Path.cwd() / "peaker_outputs"
    if not outdir.exists():
        outdir.mkdir()

    return Output(outdir, tests_ran, oldest_date.date(), latest_date.date(), [], [])

