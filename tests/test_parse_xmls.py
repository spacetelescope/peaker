import pytest
from pathlib import Path
from datetime import datetime

from peaker.parse_xmls import parse_xmls


@pytest.mark.parametrize("mission", ["jwst", "roman"])
def test_parse_xmls(mission):
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data" / mission

    # Test the function
    output = parse_xmls(data_dir, "America/New_York")

    # Set the expected oldest and latest dates
    date_format = "%Y-%m-%d"
    expected_oldest_date = datetime.strptime("2026-02-09", date_format)
    expected_latest_date = datetime.strptime("2026-02-13", date_format)
    # Make sure the dates are in local time
    expected_oldest_date = expected_oldest_date.astimezone().date()
    expected_latest_date = expected_latest_date.astimezone().date()

    assert len(output.tests_ran) == 5
    assert output.local_sdate == expected_oldest_date
    assert output.local_edate == expected_latest_date


def test_parse_0_xmls(tmpdir):
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data" / "jwst"

    # test that there are no XML files in directory
    pytest.raises(SystemExit, lambda: parse_xmls(tmpdir, "America/New_York"))

    # remove peakmem data so there is no data to use
    files = ["snippet1.xml", "snippet2.xml"]
    for xml in files:
        new_file = tmpdir / xml
        with open(new_file, "w") as nf:
            with open(str(data_dir / xml), "r") as f:
                for line in f.readlines():
                    if "properties" in line or "property" in line:
                        # this skips the block that contains the peakmem data
                        continue
                    nf.write(line)

    pytest.raises(SystemExit, lambda: parse_xmls(tmpdir, "America/New_York"))

