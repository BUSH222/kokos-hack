#!/bin/bash

FLASK_APP=main.py flask run --port=5000 &

FLASK_APP=asset_delivery.py flask run --port=5001 &

FLASK_APP=admin_app.py flask run --port=5002 &

wait