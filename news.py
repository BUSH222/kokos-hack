from flask import request, flash, redirect, Blueprint
import requests
from werkzeug.utils import secure_filename
from logger import log_event

app_news = Blueprint('app_news', __name__)


@app_news.route("/forum/new-post")
def forum_new_post():
    if 'file' not in request.files:
        log_event('No file part', 20)
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        log_event('No selected file', 20)
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        upload_url = settings["asset_delivery_ip"]
        # Prepare the files dictionary for the POST request
        files = {'file': (file.name, file.stream, file.mimetype)}
        # Send the POST request to the other microservice
        data = {'img_name': filename}
        response = requests.post(upload_url, files=files, data=data)
        print(response.status_code)
        if response.status_code == 200:
            log_event("image upload success", 10)
            return 'Success', 200
        else:
            log_event("image upload error", 30, data=data, files=files)
            return 'Failed to upload image', 500