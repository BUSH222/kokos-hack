#!/bin/bash

FLASK_APP=main.py flask run --port=5000 &

FLASK_APP=asset_delivery/asset_delivery.py flask run --port=5001 &

FLASK_APP=admin_panel/admin_app.py flask run --port=5002 &

wait

kill -9 $(lsof -t -i:5000)
kill -9 $(lsof -t -i:5001)
kill -9 $(lsof -t -i:5002)
