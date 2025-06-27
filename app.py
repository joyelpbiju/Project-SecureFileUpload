from flask import Flask, request, render_template, jsonify, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from datetime import datetime


load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_IP = os.getenv('ALLOWED_IP')
API_KEY = os.getenv('API_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('db', exist_ok=True)

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    filename = db.Column(db.String(200))
    extension = db.Column(db.String(20))
    client_ip = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def allowed_client_ip():
    client_ip = request.remote_addr
    return client_ip == ALLOWED_IP or client_ip == '127.0.0.1' or client_ip.startswith('172.')

def check_api_key():
    key = request.headers.get('X-API-KEY')
    return key == API_KEY

def log_action(action, filename):
    extension = os.path.splitext(filename)[1].lstrip('.')
    client_ip = request.remote_addr
    log_entry = LogEntry(action=action, filename=filename, extension=extension, client_ip=client_ip)
    db.session.add(log_entry)
    db.session.commit()

def get_file_info(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    size = os.path.getsize(filepath)
    ext = os.path.splitext(filename)[1].lstrip('.')
    upload_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'name': filename,
        'type': ext,
        'size': f'{round(size/1024,2)} KB',
        'upload_time': upload_time
    }

@app.before_request
def restrict_ip_and_key():
    if request.endpoint in ['index', 'uploaded_file']:
        return
    if request.endpoint in ['upload', 'delete']:
        if not allowed_client_ip():
            abort(403, description="Access Denied: Invalid IP")
        if not check_api_key():
            abort(401, description="Unauthorized: Invalid API Key")

@app.route('/')
def index():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        try:
            files.append(get_file_info(filename))
        except Exception:
            continue
    file_count = len(files)
    return render_template('index.html', files=files, file_count=file_count, api_key=API_KEY)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    log_action('Upload', filename)
    return jsonify({'status': 'success', 'message': f'File {filename} uploaded.'})

@app.route('/delete', methods=['POST'])
def delete():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'status': 'fail', 'message': 'Filename required'}), 400
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        log_action('Delete', filename)
        return jsonify({'status': 'success', 'message': f'File {filename} deleted.'})
    else:
        return jsonify({'status': 'fail', 'message': f'File {filename} not found.'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
