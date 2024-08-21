# Qualtrics Export

Code for extracting survey responses from Qualtrics using their API
which can be exercised as a command-line tool.

## Authentication

This version of the code uses [API token
authentication](https://api.qualtrics.com/2b4ffbd8af74e-api-key-authentication),
but should also be compatible with OAuth authentication as well.

The API key should be made available to the code as a
`QUALTRICS_API_KEY` environment variable. You must also provide a
`QUALTRICS_HOST` environment variable as described in the *Getting
Your API URL* section of the [Qualtrics API Quick
Start](https://api.qualtrics.com/24d63382c3a88-api-quick-start).

## Stages

### List Surveys

This part of the code requests the list of available surveys and then
filters it based on name. The underlying API can also be used to make
requests for specific surveys, filter by date, etc. but that is not
provided in the example code. The Survey ID is what is needed to
request an export.

## Request Export

An export needs to be requested before it can be downloaded. The
`request_result_export` function takes a Survey ID and returns a
Progress ID that is used to check on the status exporting process.

The format of the export can be specified. The script is currently set
to return newline-delimited JSON data (`ndjson`). There are also
options for `csv` and `json` among others. If you request a export
type other than `ndjson` then `get_export_response_data` needs to be
modified to read the appropriate type for saving.

## Check for Export Completion

There is a function `check_export_progress` that returns a status
string that is `"inProgress"`, `"failed"`, or `"complete"`. It also
returns a File ID if the progress is complete.

## Get Response Data

The function `get_export_response_data` takes the Survey ID and the
File ID and downloads the data into actual data items, rather than as
a ZIP file for flexibility.

## Processing Multiple Surveys

The function `export_surveys` takes a list of surveys returned by the
survey querying endpoint and requests exports for each survey, storing
the progress ID in the survey object/dictionary.

I didn't implement a try/wait/retry harness, but that can be
implemented using `check_and_get_response`. The function
`download_surveys` will download each survey in the list and write it
to a JSONL file in the [`data/`](data) directory if has completed. It
will print a warning message if the status is not complete.

## Command-Line Usage

### Top-Level Commands

```
usage: qualtrics_export.py [-h] {list,export,check,download} ...

List, export, and download Qualtrics surveys

positional arguments:
  {list,export,check,download}
                        Choose mode: list, export, download
    list                List available surveys
    export              Export survey specified by ID
    check               Check the status of survey response export
    download            Download the data for exported surveys
```

### Export

```
usage: qualtrics_export.py export [-h] survey_id

positional arguments:
  survey_id   The ID of the survey to be exported.
```

### Check

```
usage: qualtrics_export.py check [-h] survey_id progress_id

positional arguments:
  survey_id    The ID of the survey to be downloaded
  progress_id  The export progress ID returned by the export step.
```

### Download

```
usage: qualtrics_export.py download [-h] survey_id progress_id

positional arguments:
  survey_id    The ID of the survey to be downloaded
  progress_id  The export progress ID returned by the export step.
```
