import os
import pytest
from pathlib import Path
from datetime import datetime

from peaker.parse_xmls import parse_xmls
from peaker.table_utils import generate_report_table


@pytest.mark.parametrize("mission", ["jwst", "roman"])
def test_generate_report_table(mission, tmpdir, expected_output):
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data" / mission

    # Move into temp dir so that the output is created in there
    os.chdir(tmpdir)

    # Set the function variables
    mission = "jwst"

    date_format = "%Y-%m-%d %H:%M:%S.%f%z"
    s_date = datetime.strptime("2026-02-09 00:07:45.258429+00:00", date_format).date()
    e_date = datetime.strptime("2026-02-13 00:07:45.258429+00:00", date_format).date()

    # Create the dictionary of the tests
    output = parse_xmls(data_dir, "America/New_York")

    # Create table of tests, versions, results, and print it in a csv file
    generate_report_table(output, mission)

    table_title = "Regression_Tests_Memory_Peaks_from_{}_to_{}".format(s_date, e_date)
    csv_file = mission.upper() + "_" + table_title+".csv"
    expected_csv_file = tmpdir / "peaker_outputs" / csv_file

    assert expected_csv_file.exists()
    assert len(output.report_table["Test_name"]) == 5
    assert output.report_table["Data_points"][0] == 2
    assert all(output.report_table) == all(expected_output.report_table)
