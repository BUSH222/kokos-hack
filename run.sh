#!/bin/bash

python3 web/main.py &

python3 assets_contain/asset_delivery/asset_delivery.py &

python3 admin_panel/admin_app.py &

wait

kill -9 $(lsof -t -i:5000)
kill -9 $(lsof -t -i:5001)
kill -9 $(lsof -t -i:5002)
