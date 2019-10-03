# Python3 Flask project

Get a service account token and grant that account access to your sheet

save the contents of the service token in a file api_credentials.json

add these to .env

    secret_key="SOMETHING"
    spreadsheet_id=""
    complete_sheet_name="Complete!A:M"
    active_sheet_name="Active!A:L"

generate secret key with:

    openssl rand -base64 24