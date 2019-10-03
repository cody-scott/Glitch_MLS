import processing
import google_service_api
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    service = google_service_api.get_service()
    processing.process(service)