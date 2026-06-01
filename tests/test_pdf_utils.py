import os
from pathlib import Path

from peaker.pdf_utils import create_pdf
from peaker.parse_xmls import parse_xmls
from peaker.table_utils import generate_report_table
from peaker.plotting import mk_plots


def test_create_pdf(tmpdir, expected_output):
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data"

    # Set the function variables
    mission = "jwst"
    py_version = "py3.12"

    # Move into temp dir so that the output is created in there
    os.chdir(tmpdir)

    # Create the dictionary of the tests
    output = parse_xmls(data_dir, "America/New_York")

    # Create table of tests, versions, results, and print it in a csv file
    generate_report_table(output, mission)

    # Make the plots
    mk_plots(output)

    # Test the function
    create_pdf(output, mission, py_version)

    pdf_name = "report_peak_mem_" + py_version + ".pdf"
    pdf_path = tmpdir / "peaker_outputs"/ pdf_name

    assert output.outdir == tmpdir / "peaker_outputs"
    assert all(output.tests_ran) == all(expected_output.tests_ran)
    assert all(output.report_table) == all(expected_output.report_table)
    assert pdf_path.exists()
