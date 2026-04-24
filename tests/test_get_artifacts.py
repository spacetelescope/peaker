
import os
import pathlib
import pytest
from datetime import datetime, UTC

from peaker.get_artifacts import get_artifacts
from peaker.tests.conftest import tmpdir


# Set variables
REPO = "jwst-pipeline-results"
PY_VERSION = "3.12"

# These dates should download only 3 files
START_DATE = datetime.strptime("2026-02-22", "%Y-%m-%d").astimezone(UTC)
END_DATE = datetime.strptime("2026-02-25", "%Y-%m-%d").astimezone(UTC)


def test_bad_credentials(tmpdir):
    # Switch into tmpdir
    os.chdir(tmpdir)

    # Create a bad credentials file
    bad_credentials_file = str(tmpdir / "bad_credentials.txt")
    with open(bad_credentials_file, "w") as f:
        f.write("user_name \n")
        f.write("api_key_here \n")

    pytest.raises(ValueError, lambda: get_artifacts(bad_credentials_file, REPO, PY_VERSION,
                                                    start_date=START_DATE, end_date=END_DATE))


def test_fake_credentials(tmpdir):
    # Switch into tmpdir
    os.chdir(tmpdir)

    # Create a fake credentials file
    fake_credentials_file = str(tmpdir/ "fake_credentials.txt")
    with open(fake_credentials_file, "w") as f:
        f.write("ART_USERNAME = user_name \n")
        f.write("ART_API_KEY = api_key_here \n")

    pytest.raises(ValueError, lambda: get_artifacts(fake_credentials_file, REPO, PY_VERSION,
                                                    start_date=START_DATE, end_date=END_DATE))


"""
Getting actual artifacts cannot be regularly tested because it requires
user credentials. However, when I used my credentials this test passes,
as expected -Maria Pena-Guerrero.

def test_get_artifacts(tmpdir):
    # Switch into tmpdir
    os.chdir(tmpdir)

    good_credentials_file = "user_credentials.txt"
    
    # Test the function
    outdir = get_artifacts(good_credentials_file, REPO, PY_VERSION,
                           start_date=START_DATE, end_date=END_DATE)

    assert type(outdir) == pathlib._local.PosixPath
    assert outdir.exists()
"""
