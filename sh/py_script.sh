#!/bin/bash

pip3 install -r flask_app/requirements.txt
PYTHONUNBUFFERED=true gunicorn flask_app/server:app