from google.oauth2 import service_account
from googleapiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/spreadsheets']
service_account_file = '.data/api_credentials.json'

def get_service():
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    return service
