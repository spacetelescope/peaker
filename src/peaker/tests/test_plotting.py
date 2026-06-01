import os
import pytest
from pathlib import Path

from peaker.parse_xmls import parse_xmls
from peaker.plotting import mk_plots


@pytest.mark.parametrize("mission", ["jwst", "roman"])
def test_create_pdf(mission, tmpdir):
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "Data" / mission

    # Move into temp dir so that the output is created in there
    os.chdir(tmpdir)

    # Create the dictionary of the tests
    output = parse_xmls(data_dir, "America/New_York")

    # Make the plots
    mk_plots(output)

    assert len(output.plots) == 5
