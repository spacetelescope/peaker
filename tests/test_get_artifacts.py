"""
The get_artifacts module cannot be regularly tested because it requires
user credentials. However, when I used my credentials this test passes,
as expected -Maria Pena-Guerrero.



import os
import pathlib
from datetime import datetime, UTC

from peaker.get_artifacts import get_artifacts


def test_get_artifacts(tmpdir):
    # Switch into tmpdir
    os.chdir(tmpdir)

    # Set variables
    credentials_file = "user_artifactory_credentials.txt"
    art_repo = "jwst-pipeline-results"
    py_version = "3.12"

    # These dates should download only 3 files
    start_date = datetime.strptime("2026-02-22", "%Y-%m-%d").astimezone(UTC)
    end_date = datetime.strptime("2026-02-25", "%Y-%m-%d").astimezone(UTC)

    # Test the function
    outdir = get_artifacts(credentials_file, art_repo, py_version,
                           start_date=start_date, end_date=end_date)

    assert type(outdir) == pathlib._local.PosixPath
    assert outdir.exists()


"""
