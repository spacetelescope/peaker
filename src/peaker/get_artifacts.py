"""Utilities to find and download .xml files from with Artifactory repository"""
import pydantic
from pyartifactory import Artifactory
from pathlib import Path


def _get_artifactory_credentials(credentials_file):
    # Artifactory Credentials
    art_username, art_api_key = None, None
    with open(credentials_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if "username" in line.lower():
                art_username = line.split("=")[1].strip()
            elif "key" in line.lower():
                art_api_key = pydantic.types.SecretStr(line.split("=")[1].strip())
            if art_username is not None and art_api_key is not None:
                break
    if art_username is None and art_api_key is None:
        raise ValueError("No credentials provided.")
    return art_username, art_api_key


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
    # Get artifactory Credentials
    art_username, art_api_key = _get_artifactory_credentials(credentials_file)

    # Do basic authentication
    art = Artifactory(url="https://bytesalad.stsci.edu/artifactory",
                      auth=(art_username, art_api_key), api_version=1)

    # Get the artifacts
    artifacts = art.artifacts.list(art_repo, depth=2)

    # Create an output directory if none was given
    if outdir is None:
        outdir = Path.cwd() / "xmls"
        if not outdir.exists():
            outdir.mkdir()

    print(" Searching Artifactory...")
    artifacts2download = {}
    for artifact in artifacts.files:
        # Proceed with download if within the desired dates
        artifact_datetime = artifact.lastModified
        if start_date is not None:
            if artifact_datetime <= start_date or artifact_datetime > end_date:
                continue

        if ".xml" in artifact.uri:
            if "jwst" in art_repo:
                # Only download if the run was in main
                if "rc" not in artifact.uri:
                    continue

            # Make sure that the file is the result of the right python version run
            if py_version not in artifact.uri:
                continue
            if artifact_datetime.date() not in artifacts2download:
                artifacts2download[artifact_datetime.date()] = [artifact]
            else:
                artifacts2download[artifact_datetime.date()].append(artifact)

    print(" Downloading .xml files...")
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

    print(" Finished downloading artifacts at: ", outdir)

    return outdir

