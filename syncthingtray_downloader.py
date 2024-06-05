"""
Downloads the latest version of SyncThingTray from GitHub. (Windows Version)

To use, you must specify the download path in a file named "download_path.txt".
"""
import os
import re
import time

import requests
import zipfile
from io import BytesIO

from githubreleasehelper import GitHubReleaseHelper

API_URL = "https://api.github.com/repos/Martchus/syncthingtray/releases/latest"
RELEASE_MATCH = r"^syncthingtray-\d+\.\d+\.\d+-x86_64-w64-mingw32\.exe\.zip$"
FILE_NAMES_REGEX = {
    re.compile(r"^syncthingtray.+-cli\.exe$"): "syncthingtraycli.exe",
    re.compile(r"^syncthingtray(?:(?!-cli).)*\.exe$"): "syncthingtray.exe",
    re.compile(r"^syncthingtray(?:(?!-cli).)*\.md$"): "syncthingtray.md"
}


class DownloadError(Exception):
    pass


def get_download_path():
    with open("download_path.txt", "r") as file:
        return file.read().rstrip()


def download_file(url: str) -> tuple[requests.Response, str]:
    request = requests.get(url)

    if request.status_code != 200:
        raise DownloadError(f"Download failed with Status Code {request.status_code} downloading from {url}.")

    # Retrieve filename
    if "Content-Disposition" in request.headers:
        content_disposition = request.headers["Content-Disposition"]
        filename = content_disposition.split("filename=")[1]
    else:
        print("[WARNING] File had no Content-Disposition header. Falling back to URL parsing.")
        filename = url.split("/")[-1]

    return request, filename


def unzip_from_bytes(zip_data: requests.Response.content, directory: str = None) -> list[str]:
    """
    Unzips a zip file from its raw bytes into the current working directory.
    :param zip_data: The content of the zip
    :param directory: Where to unzip the contents to.
    :return: Filenames of the extracted contents
    """
    # Unzip the file
    with zipfile.ZipFile(BytesIO(zip_data), "r") as zip_ref:
        filenames = zip_ref.namelist()

        if directory is None:
            zip_ref.extractall()
        else:
            zip_ref.extractall(directory)

    return filenames


def main():
    start_time = time.time()

    # Get where to download the file, fallback to current working directory if not found
    try:
        download_path = get_download_path()
    except FileNotFoundError:
        print("[WARNING] download_path.txt not found. Falling back to current working directory.")
        download_path = os.getcwd()

    github_helper = GitHubReleaseHelper(API_URL)
    print(f"[INFO] Found SyncThingTray {github_helper.get_latest_version()}")

    # Get the info to the latest asset matching our regex
    release_info = github_helper.get_download_regex(RELEASE_MATCH)

    # Download the file
    print(f"[INFO] Downloading from {release_info['browser_download_url']}...")
    response, filename = download_file(release_info["browser_download_url"])
    print(f"[INFO] Downloaded file: {filename}\n")

    # Unzip the file
    filenames = unzip_from_bytes(response.content, download_path)

    # Rename the files
    for filename in filenames:
        for regex, filename_map in FILE_NAMES_REGEX.items():
            if regex.fullmatch(filename):
                # Delete first if it exists already
                orig_file_path = os.path.join(download_path, filename)
                file_path = os.path.join(download_path, filename_map)

                if os.path.exists(file_path):
                    print(f"[INFO] Deleting existing file {filename_map}")
                    os.remove(file_path)

                print(f"[INFO] Renaming {filename} to {filename_map}")
                os.rename(orig_file_path, file_path)
                break

    print(f"\n[INFO] Done! Elapsed Time: {time.time() - start_time}s")


if __name__ == '__main__':
    main()
