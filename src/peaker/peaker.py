"""Main module"""

import sys
import argparse
from datetime import datetime, timedelta, UTC, timezone
from pathlib import Path

from peaker.get_artifacts import get_artifacts
from peaker.parse_xmls import parse_xmls
from peaker.plotting import mk_plots
from peaker.table_utils import generate_report_table
from peaker.pdf_utils import create_pdf
from peaker.jwst_utils import ART_JWST_REPO, POOLS_JWST
from peaker.roman_utils import ART_ROMAN_REPO, POOLS_ROMAN


def main():
    parser = argparse.ArgumentParser(description="Display peak memory history for Regression Tests.")
    parser.add_argument("art_credentials",
                        action="store",
                        help="File with Artifactor credentials.")
    parser.add_argument("--xmldir", "-x",
                        action="store",
                        default=None,
                        help="Path of the directory to save/read the XML files.")
    parser.add_argument("--mission", "-m",
                        action="store",
                        default="jwst",
                        help="Name of the mission to analyze, i.e. -m=jwst")
    parser.add_argument("--days", "-d",
                        action="store",
                        default=None,
                        type=int,
                        help="Number of days to show, e.g. -d=5 will show today and the last 4 days back. Default is"
                             "None.")
    parser.add_argument("--period", "-p",
                        action="store",
                        default=None,
                        help="Period of time to show. Input should be start to end, in the format year-month-day, "
                             "local time, e.g. -p=2026-01-23to2026-02-27. Default is download everything up to today.")
    parser.add_argument("--timezone", "-t",
                        dest="localtz",
                        action="store",
                        default="EST",
                        help="Timezone to convert UTC time from xml files in the plots and report, e.g. -t=GMT. "
                             "The code takes all IANA time zone strings.")
    parser.add_argument("--version", "-v",
                        dest="py_version",
                        action="store",
                        default="3.12",
                        help="Python version tested in the regression tests, e.g. -v=3.11")
    parser.add_argument("-s",
                        dest="skip_download_artifacts",
                        action="store_true",
                        default=False,
                        help="Use flag -s to skip downloading artifacts and just read from xmldir.")

    args = parser.parse_args()

    # Define variables
    credentials_file = args.art_credentials
    xmldir = args.xmldir
    mission = args.mission
    days = args.days
    period = args.period
    localtz = args.localtz
    py_version = "py" + args.py_version
    skip_download_artifacts = args.skip_download_artifacts

    # Get the path where to find xml files
    if xmldir is not None:
        xmldir = Path(xmldir)

    # Get the appropriate Artifactory repo name and the
    # corresponding description of pool tests
    if mission == "jwst":
        art_repo = ART_JWST_REPO
        pools = POOLS_JWST
    elif mission == "roman":
        art_repo = ART_ROMAN_REPO
        pools = POOLS_ROMAN

    # Set the start and end dates in UTC
    start_date, end_date = None, None
    if days is not None:
        start_date = datetime.now(UTC) - timedelta(days=days)
        end_date = datetime.now(UTC)
    elif period is not None:
        start_date = period.split("to")[0]
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.astimezone(timezone.utc)
        end_date = period.split("to")[1]
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.astimezone(timezone.utc)

    # Sanity check
    if end_date < start_date:
        print("Start date must be before end date. Switching start date to end date and vice versa.")
        new_end_date = start_date
        new_start_date = end_date
        start_date = new_start_date
        end_date = new_end_date

    # Get relevant xml files from artifactory
    if not skip_download_artifacts:
        xmldir = get_artifacts(credentials_file, art_repo, py_version,
                               outdir=xmldir, start_date=start_date, end_date=end_date)
    else:
        if xmldir is None:
            raise ValueError("No XML directory specified.")

    # Store memory info in a dictionary of test name and points per date
    output = parse_xmls(xmldir, localtz)

    # Create table of tests, versions, results, and print it in a csv file
    generate_report_table(output, mission, pools=pools)

    # Make the plots
    mk_plots(output)

    # Create PDF report with table and plots
    create_pdf(output, mission, py_version)

    print("\nFinished! \n")


if __name__ == "__main__":
    sys.exit(main())
