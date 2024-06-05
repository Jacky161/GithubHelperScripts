"""
Library to help interface with the GitHub API. Has the capability to download a file matching a regex for the filename.
"""

# Use REST APIs
import requests
import re
from typing import Any


class GitHubReleaseHelper:
    def __init__(self, url: str) -> None:
        """
        :param url: API URL to the latest release. (https://api.github.com/repos/$AUTHOR/$REPO/releases/latest)
        """
        self.api_url = url

    def get_latest_release(self) -> dict[str, Any]:
        """
        Returns the latest release info from the GitHub API.
        """
        # Get data from GitHub
        release_data = requests.get(self.api_url).json()
        return release_data

    def get_latest_version(self) -> str:
        """
        Returns the latest release version from the GitHub API.
        """

        release_data = self.get_latest_release()

        return release_data["name"]

    def get_download_regex(self, regex: str) -> dict[str, Any]:
        """
        Returns the download URL for a file given regex.
        :param regex: The regex string to match the filename with.
        :return: The asset for the file matching the regex.
        """
        release_match = re.compile(regex)
        release_data = self.get_latest_release()

        # Try to find the matching asset
        for asset in release_data["assets"]:
            if release_match.fullmatch(asset["name"]):
                return asset

        raise MissingAssetError(f'Could not find matching asset for "{regex}"')


class MissingAssetError(Exception):
    pass
