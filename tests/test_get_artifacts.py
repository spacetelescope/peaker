
import os
import pytest
import pathlib
from datetime import datetime, UTC, tzinfo, timezone, timedelta
from dataclasses import dataclass

from peaker.get_artifacts import get_artifacts, _filter_artifacts, _list_artifacts
from .conftest import tmpdir



# Set variables
REPO = "jwst-pipeline-results"
PY_VERSION = "3.12"

# These dates should download only 3 files
START_DATE = datetime.strptime("2026-02-22", "%Y-%m-%d").astimezone(UTC)
END_DATE = datetime.strptime("2026-02-25", "%Y-%m-%d").astimezone(UTC)


def test_bad_credentials(tmpdir):
    """Test the credentials file when the expected variables are not present at all."""
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
    """Test the credentials file when the expected variables are present but have invalid values."""
    # Switch into tmpdir
    os.chdir(tmpdir)

    # Create a fake credentials file
    fake_credentials_file = str(tmpdir/ "fake_credentials.txt")
    with open(fake_credentials_file, "w") as f:
        f.write("ART_USERNAME = user_name \n")
        f.write("ART_API_KEY = api_key_here \n")

    pytest.raises(ValueError, lambda: get_artifacts(fake_credentials_file, REPO, PY_VERSION,
                                                    start_date=START_DATE, end_date=END_DATE))


@dataclass
class Art:
    uri: str
    created: datetime
    files: list

@dataclass
class ArtifactListFolderResponse:
    uri: str
    size: int
    lastModified: datetime
    folder: bool

@dataclass
class ArtifactListFileResponse:
    uri: str
    size: int
    lastModified: datetime
    folder: bool
    sha1: str
    sha2: str

def mk_artifact(credentials_file="file.txt", art_repo="jwst-pipeline-results"):
    """Creates fake artifact for testing."""
    art = Art(art_repo,
               datetime(2026, 5, 29, 12, 37, 46, 9000,
                        tzinfo=tzinfo(-14400)),
               [ArtifactListFolderResponse(uri='/2025-08-28_GITHUB_CI_Linux-X64-py3.12-2600', size=-1,
                                           lastModified=datetime(2025, 8, 28, 14,
                                                                 4, 1, 931000,
                                                                tzinfo=timezone(timedelta(hours=-4))), folder=True),
                ArtifactListFileResponse(
                    uri='/2025-08-28_GITHUB_CI_Linux-X64-py3.12-2600/results-jwst-1.19.0rc0-313-g33fd00a1c-Linux-X64-py3.12-2600.xml',
                    size=557443, lastModified=datetime(2025, 8, 28, 14,
                                                       4, 1, 915000,
                                                       tzinfo=timezone(timedelta(hours=-4))),
                    folder=False, sha1='ae3176fb78176659afe47', sha2='a547794d7fd5ea17ccd4edb81b7b4ca'),
                ArtifactListFileResponse(
                   uri='/2025-08-28_GITHUB_CI_Linux-X64-py3.12-2600/snapshot-jwst-1.19.0rc0-313-g33fd00a1c-Linux-X64-py3.12-2600.yml',
                   size=6094, lastModified=datetime(2025, 8, 28, 14,
                                                    4, 2, 157000,
                                                    tzinfo=timezone(timedelta(hours=-4))),
                   folder=False, sha1='f43331ea75fc31d6daac', sha2='fefbf84818f35a1cf04addc25635e'),
                ArtifactListFileResponse(
                   uri='/2025-08-28_GITHUB_CI_Linux-X64-py3.12-2600/summary-jwst-1.19.0rc0-313-g33fd00a1c-Linux-X64-py3.12-2600.md',
                   size=100, lastModified=datetime(2025, 8, 28, 14,
                                                   4, 2, 46000,
                                                   tzinfo=timezone(timedelta(hours=-4))),
                   folder=False, sha1='e3c35f199da13d31da896', sha2='ea67c9a04f9547b42ddfb2148caf5959')]
               )
    # The real function will return the artifactory instance and the filtered info, to mock it
    # we just need another object of similar characteristics
    return art, art


def test_get_artifacts(tmpdir, monkeypatch):
    """Test the creation of an output directory with a fake artifact."""
    # Switch into tmpdir
    os.chdir(tmpdir)

    # Test the function
    monkeypatch.setattr("src.peaker.get_artifacts._list_artifacts", mk_artifact)
    outdir = get_artifacts("user_credentials.txt", REPO, PY_VERSION,
                           start_date=START_DATE, end_date=END_DATE)

    assert type(outdir) == pathlib._local.PosixPath
    assert outdir.exists()


def test_filter_artifacts(tmpdir):
    """Test that only xml files are filtered from the fake artifact."""
    _, artifacts = mk_artifact()
    start_date = datetime(2025, 8, 27, 14, 4, 1, 915000,
                          tzinfo=timezone(timedelta(hours=-4)))
    end_date = datetime(2025, 8, 29, 14, 4, 1, 915000,
                        tzinfo=timezone(timedelta(hours=-4)))
    py_version = "py3.12"
    artifacts2download = _filter_artifacts("jwst-pipeline-results", artifacts, start_date, end_date, py_version)

    assert len(artifacts2download) == 1
