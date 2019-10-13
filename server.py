from flask import Flask, request, render_template, redirect
import google_service_api
from dotenv import load_dotenv
load_dotenv()

import os

app = Flask(__name__)

import json
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
    mp = mapping.get_mappings()
    return mp


@app.route('/map-{}'.format(os.getenv('spreadsheet_id')))
def view_get_map():
    return render_template('map.html')


@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")


if __name__ == "__main__":
    app.run()
