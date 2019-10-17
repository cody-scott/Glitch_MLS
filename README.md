# Python and Nodejs

Running both python (flask) and nodejs (express) in one app

Python used for server and all processing work
Nodejs is used for estimation of prices using turfjs


## setup

Get a service account token and grant that account access to your sheet

save the contents of the service token in a file 

    .data/api_credentials.json

add these to .env

    secret_key="SOMETHING"
    spreadsheet_id=""
    complete_sheet_name="Complete!A:M"
    active_sheet_name="Active!A:L"

generate secret key with:

    openssl rand -base64 24