"""A command-line tool to demonstrate listing, exporting, and
downloading the data from Qualtrics surveys.

* List the set of available surveys:
    python qualtrics_export.py list

* Export a survey based on ID:
    python qualtrics_export.py export <survey-id>"""

import argparse
import requests
import os
from io import BytesIO
import jsonlines
from zipfile import ZipFile
from pprint import pprint

# You need to set QUALTRICS_HOST and QUALTRICS_API_KEY
# environment variables for your Qualtrics instance.
# You can find an overview of how to determine them here:
# https://api.qualtrics.com/24d63382c3a88-api-quick-start
#
QUALTRICS_HOST = os.getenv("QUALTRICS_HOST")
QUALTRICS_API_KEY = os.getenv("QUALTRICS_API_KEY")

BASE_URL = f"https://{QUALTRICS_HOST}/API/v3"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-TOKEN": QUALTRICS_API_KEY,
}


def main():
    args = command_line_parser().parse_args()
    if args.mode == "list":
        survey_list = list_surveys()
        pprint(survey_list)
    elif args.mode == "export":
        survey_id = args.survey_id
        print(f"Requestion export of {survey_id}...")
        progress_id = request_result_export(survey_id)
        print(f"Progress ID: {progress_id}")
    elif args.mode == "check":
        survey_id = args.survey_id
        progress_id = args.progress_id
        print(f"Checking status of export of {survey_id}/{progress_id}...")
        status, file_id = check_export_progress(survey_id, progress_id)
        print(f"Export status: {status} {file_id}")
    elif args.mode == "download":
        survey_id = args.survey_id
        progress_id = args.progress_id
        print(f"Checking, maybe downloading {survey_id}/{progress_id}...")
        download_survey(survey_id, progress_id)

        
def command_line_parser():
    parser = argparse.ArgumentParser(
        description="List, export, and download Qualtrics surveys"
    )
    mode_parser = parser.add_subparsers(
        dest="mode",
        required=True,
        help="Choose mode: list, export, download",
    )
    mode_parser.add_parser("list", help="List available surveys")
    export_parser = mode_parser.add_parser(
        "export",
        help="Export survey specified by ID",
    )
    export_parser.add_argument(
        "survey_id",
        type=str,
        help="The ID of the survey to be exported.",
    )
    download_parser = mode_parser.add_parser(
        "check",
        help="Check the status of survey response export",
    )
    download_parser.add_argument(
        "survey_id",
        type=str,
        help="The ID of the survey to be downloaded",
    )
    download_parser.add_argument(
        "progress_id",
        type=str,
        help="The export progress ID returned by the export step.",
    )
    download_parser = mode_parser.add_parser(
        "download",
        help="Download the data for exported surveys",
    )
    download_parser.add_argument(
        "survey_id",
        type=str,
        help="The ID of the survey to be downloaded",
    )
    download_parser.add_argument(
        "progress_id",
        type=str,
        help="The export progress ID returned by the export step.",
    )
    return parser
    
        
def list_surveys():
    """Return a list of all known surveys."""
    r = requests.get(f"{BASE_URL}/surveys", headers=HEADERS)
    r.raise_for_status()
    rj = r.json()
    survey_list = rj["result"]["elements"]
    return survey_list


def request_result_export(survey_id):
    r = requests.post(
        f"{BASE_URL}/surveys/{survey_id}/export-responses",
        headers=HEADERS,
        json={"format": "ndjson"},
    )
    r.raise_for_status()
    rj = r.json()
    progress_id = rj["result"]["progressId"]
    return progress_id


def download_survey(survey_id, progress_id):
    """Check if the export for the survey is finished and, if so, download."""
    print(f"Attempting to get response data '{survey_id}'/{progress_id}...")
    status, zip_file = check_and_get_responses(survey_id, progress_id)
    if status == "complete":
        print(f"Read data as {zip_file.namelist()}")
        write_survey_data(zip_file)
    else:
        print(
            f"Warning: survey export '{survey_id}/{progress_id}' not completed: {status}"
        )


def check_and_get_responses(survey_id, progress_id):
    status, file_id = check_export_progress(survey_id, progress_id)
    if status == "complete":
        zip_file = get_export_response_data(survey_id, file_id)
    else:
        zip_file = None
    return status, zip_file


def check_export_progress(survey_id, progress_id):
    r = requests.get(
        f"{BASE_URL}/surveys/{survey_id}/export-responses/{progress_id}",
        headers=HEADERS,
    )
    r.raise_for_status()
    rj = r.json()
    status = rj["result"]["status"]
    file_id = rj["result"].get("fileId", None)
    return status, file_id


def get_export_response_data(survey_id, file_id):
    r = requests.get(
        f"{BASE_URL}/surveys/{survey_id}/export-responses/{file_id}/file",
        headers=HEADERS,
        stream=True,
    )
    r.raise_for_status()
    zip_file = ZipFile(BytesIO(r.content))
    return zip_file


def write_survey_data(zip_file):
    # The zip file or the contents of the zip file can be
    # written out to the file system, or it can be read
    # directly into data objects as in the commented-out code.
    file_name = zip_file.namelist()[0]

    # Write to local file
    print(f"Writing survey data to {file_name}...")
    zip_file.extract(file_name)

    # Alternative: Read into data records
    # with jsonlines.Reader(zip_file.open(file_name)) as in_file:
    #     json_recs = [resp for resp in in_file]


if __name__ == "__main__":
    main()
