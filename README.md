# Qualtrics Export

Code for extracting survey responses from Qualtrics using their API.

## Authentication

This version of the code uses [API token
authentication](https://api.qualtrics.com/2b4ffbd8af74e-api-key-authentication),
but should also be compatible with OAuth authentication as well.

You can copy the [`.env.default`](.env.default) to `.env` and fill in
your `QUALTRICS_API_KEY` which will get picked up by `load_dotenv`.

## Stages

### Identify Surveys

This script requests the list of available surveys and then filters it
based on name. You can also make requests for specific surveys, filter by
date, etc. The Survey ID is what is needed to request an export.

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

