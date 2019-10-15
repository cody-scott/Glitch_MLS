from flask import Flask, request, render_template, redirect, jsonify, has_request_context
from flask_cors import CORS
import google_service_api
from dotenv import load_dotenv
load_dotenv()

import os

app = Flask(__name__)
cors = CORS(app)

import datetime
nw = datetime.datetime.now()
log_file = os.path.join(".data/logs", "Log_{}{}{}".format(nw.year, nw.month, nw.day))

import logging
root = logging.getLogger()

from logging import Formatter
class RequestFormatter(Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            print(request.environ.get('HTTP_X_FORWARDED_FOR', "NOADDR"))
            record.remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s]\t%(remote_addr)s requested %(url)s\t%(levelname)s\t%(module)s\t%(message)s'
)

from flask.logging import default_handler
default_handler.setFormatter(formatter)
root.addHandler(default_handler)
root.setLevel(logging.INFO)

f_handler = logging.FileHandler(log_file)
f_handler.setFormatter(formatter)
f_handler.setLevel(logging.INFO)
root.addHandler(f_handler)

import processing
import mapping

def _valid_secret_key(method=None):
    sk = request.headers.get('secret_key')
    if method == "POST":
        sk = request.json.get('secret_key')

    if sk == os.getenv("secret_key"):
        return True
    else:
        return False


@app.route("/", methods=['POST', 'GET'])
def hello():
    req = request
    if request.method == 'GET':
        return "Hello world!"
    req = request

    env = os.environ
    headers = request.headers
    
    sk = request.json['secret_key']
    if sk != os.getenv("secret_key"):
        return "Hello world!"

    service = google_service_api.get_service()
    processing.process(service)

    return "Completed"


@app.route('/mapData-{}'.format(os.getenv('spreadsheet_id')))
def view_get_map_data():
    mp = mapping.get_mappings(450000)
    return mp


@app.route('/mapData-Collected-{}'.format(os.getenv('spreadsheet_id')))
def view_get_collected_map_data():
    req = request
    mp = mapping.get_unique_lat_long()
    return mp


@app.route('/map-{}'.format(os.getenv('spreadsheet_id')))
def view_get_map():
    return render_template('map.html')


@app.route('/mapData-CSV-{}'.format(os.getenv('spreadsheet_id')))
def view_get_all_map_data():    
    service = google_service_api.get_service()
    df = processing.current_listings_csv(service)
    return df
  
@app.route('/mapData-JSON-{}'.format(os.getenv('spreadsheet_id')))
def view_get_all_map_data_json():    
    service = google_service_api.get_service()
    df = processing.current_listings_csv(service, "JSON")
    # return jsonify(df)
    return df
  
@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")


if __name__ == "__main__":
    app.run()
