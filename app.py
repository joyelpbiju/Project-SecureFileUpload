from flask import Flask, request, render_template, jsonify, abort
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_IP = os.getenv('ALLOWED_IP')
API_KEY = os.getenv('API_KEY')


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_client_ip():
    client_ip = request.remote_addr
    return client_ip == ALLOWED_IP or client_ip == '127.0.0.1' or client_ip.startswith('172.')

def check_api_key():
    key = request.headers.get('X-API-KEY')
    return key == API_KEY

@app.before_request
def restrict_ip_and_key():

    if request.endpoint == 'index':
        return

    if request.endpoint in ['upload', 'delete']:
        if not allowed_client_ip():
            abort(403, description="Access Denied: Invalid IP")
        if not check_api_key():
            abort(401, description="Unauthorized: Invalid API Key")

@app.route('/')
def index():
    return render_template('index.html', api_key=API_KEY)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'status': 'success', 'message': f'File {filename} uploaded successfully.'})

@app.route('/delete', methods=['POST'])
def delete():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'status': 'fail', 'message': 'Filename required'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'status': 'success', 'message': f'File {filename} deleted.'})
    else:
        return jsonify({'status': 'fail', 'message': f'File {filename} not found.'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
