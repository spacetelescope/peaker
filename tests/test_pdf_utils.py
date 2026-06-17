import os
import pytest
from pathlib import Path

from peaker.pdf_utils import create_pdf, _get_plt_path, _select_cols
from peaker.parse_xmls import parse_xmls
from peaker.table_utils import generate_report_table
from peaker.plotting import mk_plots


@pytest.mark.parametrize("mission", ["jwst", "roman"])
def test_create_pdf(mission, tmpdir, expected_output):
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data" / mission

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
    assert pdf_path.stat().st_size > 7500


def test_get_plt_path(tmpdir, mk_plotsdir):
    """Test reconstruction of plot name in plots directory."""

    truth_name = "std[pool_004_wfs]_M_associations_sdp_pools.png"
    expected = tmpdir / "peaker_outputs" / "plots" / truth_name

    plots = [tmpdir / "peaker_outputs" / "plots" / truth_name]
    test_name = "std[pool_004_wfs]"
    test_class = "associations_sdp_pools"
    plt_name = _get_plt_path(plots, test_name, test_class)

    assert plt_name == expected


def test_select_cols(expected_table):
    """Test that the columns for the PDF are selected."""
    selected_cols, col_widths = _select_cols(expected_table)
    # test number of columns is 7
    assert len(selected_cols[0]) == 7
    # test data points is 2
    assert selected_cols[-2][-2] == "2"
    # test the colum widths returned adds up to 100
    assert sum(col_widths) == 100
