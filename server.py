from flask import Flask, request, render_template, redirect, jsonify
from flask_cors import CORS
import google_service_api
from dotenv import load_dotenv
load_dotenv()

import os

app = Flask(__name__)
cors = CORS(app)

from _log import setup_logger
setup_logger()
app.logger.info("Starting New App")

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
    r = request
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
