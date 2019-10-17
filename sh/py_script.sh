#!/bin/bash

pwd
pip3 install -r flask_app/requirements.txt --user
PYTHONUNBUFFERED=true python3 flask_app/server.py