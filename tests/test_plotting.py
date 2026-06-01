import os
from pathlib import Path

from peaker.parse_xmls import parse_xmls
from peaker.plotting import mk_plots


def test_create_pdf(tmpdir):
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data"

    # Move into temp dir so that the output is created in there
    os.chdir(tmpdir)

    # Create the dictionary of the tests
    output = parse_xmls(data_dir, "America/New_York")

    # Make the plots
    mk_plots(output)

    assert len(output.plots) == 5
