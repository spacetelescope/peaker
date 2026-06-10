"""Utilities to find and download .xml files from with Artifactory repository"""

import requests
import pydantic
import pyartifactory
from pathlib import Path


def _get_artifactory_credentials(credentials_file):
    # Artifactory Credentials
    art_username, art_api_key = None, None
    with open(credentials_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            try:
                value = line.split("=")[1].strip()
            except IndexError:
                raise ValueError("Bad Artifactory credentials provided.")
            if "username" in line.lower():
                art_username = value
            elif "key" in line.lower():
                art_api_key = pydantic.types.SecretStr(value)
            if art_username is not None and art_api_key is not None:
                break
    if art_username is None and art_api_key is None:
        raise ValueError("No credentials found.")
    return art_username, art_api_key


def _list_artifacts(credentials_file, art_repo):
    # Get artifactory Credentials
    art_username, art_api_key = _get_artifactory_credentials(credentials_file)

    try:
        # Do basic authentication
        art = pyartifactory.Artifactory(url="https://bytesalad.stsci.edu/artifactory",
                                        auth=(art_username, art_api_key), api_version=1)
    # catch a timeout connection issue or a pyartifactory error and exit gracefully 
    except (requests.exceptions.ConnectTimeout, pyartifactory.exception.ArtifactoryError):
        exit()

    # Get the artifacts with user credentials
    artifacts = art.artifacts.list(art_repo, depth=2)

    return art, artifacts


def _filter_artifacts(artifacts, start_date, end_date, py_version):
    artifacts2download = {}
    for artifact in artifacts.files:
        # Proceed with download if within the desired dates
        artifact_datetime = artifact.lastModified
        if start_date is not None:
            if artifact_datetime <= start_date or artifact_datetime > end_date:
                continue

        if ".xml" in artifact.uri:
            # Make sure that the file is the result of the right python version run
            if py_version not in artifact.uri:
                continue
            if artifact_datetime.date() not in artifacts2download:
                artifacts2download[artifact_datetime.date()] = [artifact]
            else:
                artifacts2download[artifact_datetime.date()].append(artifact)

    return artifacts2download


def _download_artifacts(art, artifacts2download, art_repo, outdir):
    # Currently, the branch information is lost when the artifact is uploaded, so take the file
    # that was last modified in the day to try and ensure that this was the automated run on main.
    for date, artifacts in artifacts2download.items():
        run_times = [artifact.lastModified.time() for artifact in artifacts]
        latest = max(run_times)
        nightly_idx = run_times.index(latest)
        artifact = artifacts[nightly_idx]
        xmlfile = art_repo + artifact.uri
        file = outdir / str(artifact.uri).split(sep="/")[-1]

        # Only download the files if not already there or the sizes do not match
        download = False
        if file.exists():
            if artifact.size > file.stat().st_size:
                download = True
        else:
            download = True
        if download:
            print(artifact.uri)
            art.artifacts.download(xmlfile, str(outdir))


def get_artifacts(credentials_file, art_repo, py_version, outdir=None, start_date=None, end_date=None):
    """
    Finds and downloads .xml files from with Artifactory repository for the given period.
    
    Parameters
    ----------
    credentials_file : str
        Path to user Artifactory credentials text file.
    art_repo : str
        Artifactory repository name.
    py_version : str
        Version of Python tested and reported.
    outdir : pathlib.Path or None
        Full path for the output directory.
    start_date : datetime.datetime
        Start date (UTC) for search and download.
    end_date : datetime.datetime
        End date (UTC) for search and download.

    Returns
    -------
    outdir : pathlib.Path
        Full path for the output directory.

    """
    art, artifacts = _list_artifacts(credentials_file, art_repo)

    # Create an output directory if none was given
    if outdir is None:
        outdir = Path.cwd() / "xmls"
        if not outdir.exists():
            outdir.mkdir()

    print(" Searching Artifactory...")
    artifacts2download = _filter_artifacts(artifacts, start_date, end_date, py_version)

    print(" Downloading .xml files...")
    _download_artifacts(art, artifacts2download, art_repo, outdir)

    print(" Finished downloading artifacts at: ", outdir)

    return outdir

