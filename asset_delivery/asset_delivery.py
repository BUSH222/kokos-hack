from flask import Flask, render_template_string, send_from_directory, request, jsonify, abort
import os
import psutil
from settings_loader import get_processor_settings
from logger import log_event
from collections import deque
import time


app = Flask(__name__)

settings = get_processor_settings()
request_timestamps = deque()


@app.before_request
def track_requests():
    """Track the timestamp of each request."""
    global request_timestamps
    current_time = time.time()
    request_timestamps.append(current_time)
    while request_timestamps and request_timestamps[0] < current_time - 60:
        request_timestamps.popleft()


@app.route('/assets/')
@app.route('/assets/<path:subpath>')
def serve_asset(subpath=''):
    """
    Serve static assets or directory listings.

    This endpoint serves files from the 'assets' directory. If the requested path
    is a directory, it returns an HTML page listing the contents of the directory.
    If the requested path is a file, it serves the file.

    Args:
        subpath (str): The subpath within the 'assets' directory. Defaults to an empty string.

    Returns:
        str: HTML content listing the directory contents if `subpath` is a directory.
        Response: The file content if `subpath` is a file.

    Example:
        Accessing `/assets/` will list the contents of the 'assets' directory.
        Accessing `/assets/test/` will list the contents of the 'assets/images' directory.
        Accessing `/assets/test/uni.png` will serve the 'uni.png' file from the 'assets/images' directory.
    """
    directory = os.path.join(app.root_path, 'assets/', subpath)
    print(directory)
    if os.path.isdir(directory):
        files = os.listdir(directory)
        file_links = [f'<li><a href="{os.path.join(subpath, file)}">{file}</a></li>' for file in files]
        current_dir = f"Directory listing for /assets/{subpath}" if subpath else "Directory listing for /assets/"

        # Determine the back link
        if subpath:
            parent_path = os.path.dirname(subpath)
            back_link = f'<li><a href="/assets/{parent_path}">back</a></li>'
        else:
            back_link = ''

        return render_template_string(f'''
            <h1>{current_dir}</h1>
            <ul>
                {''.join(file_links)}
                <br>
                {back_link}
            </ul>
        ''')
    else:
        log_event(f"Served asset {subpath}", 10)
        return send_from_directory('assets', subpath)


@app.route('/upload_assets', methods=['POST'])
def upload_image():
    """
    Upload an image from other microservices, specifically admin_app to this server

    Args:
        request.files['file']
    Returns:
        json: {"msg": "Unauthorised"} when accessing from an unauthorised ip
        json: {"msg": "File uploaded Successfully"} when accessing from an unauthorised ip
    """
    allowed_ips = settings["allowed_ips"]
    print(request.remote_addr)
    if request.remote_addr not in allowed_ips:
        return jsonify({"msg": "Unauthorized"}), 403

    file = request.files['file']
    name = request.form.get('img_name')
    print(request.form)
    print(request.files)
    # Save the file to the /assets/ directory
    file.save(os.path.join(app.root_path, 'assets', name))
    log_event("file uploaded successfully", 10)
    return jsonify({"msg": "File uploaded successfully"}), 200


@app.route('/asset_delivery_server_status', methods=['GET'])
def asset_delivery_server_status():
    """
    Shows the current RAM and CPU usage of the server, can only be accessed by localhost ips
    Returns:
        abort(403): accessed from the wrong ip
        json: {'ram': , 'cpu': } ram and cpu usage percent with a comment
    """
    allowed_ips = settings["allowed_ips"]
    if request.remote_addr not in allowed_ips:
        return abort(403)
    return jsonify({'ram': psutil.virtual_memory().percent,
                    'cpu': psutil.cpu_percent(),
                    'rpm': len(request_timestamps)})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
