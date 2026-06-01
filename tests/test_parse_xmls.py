from pathlib import Path
from datetime import datetime

from peaker.parse_xmls import parse_xmls


def test_parse_xmls():
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data"

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

