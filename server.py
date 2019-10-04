from flask import Flask, request
import google_service_api
from dotenv import load_dotenv
load_dotenv()

import os

app = Flask(__name__)


import json
import processing


@app.route("/", methods = ['POST', 'GET'])
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


if __name__ == "__main__":
    app.run()
