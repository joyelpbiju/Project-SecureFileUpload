from flask import Flask, request, render_template, jsonify, abort, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Load .env
load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
API_KEY = os.getenv('API_KEY')

# Multi-IP Support
ALLOWED_IPS = os.getenv('ALLOWED_IPS', '').split(',')
ALLOWED_EXTENSIONS = {'.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heif', '.raw', '.svg', '.psd'}

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
    status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def allowed_client_ip():
    client_ip = request.remote_addr
    clean_ips = [ip.strip() for ip in ALLOWED_IPS if ip.strip()]
    return client_ip in clean_ips or client_ip == '127.0.0.1' or client_ip.startswith('172.')

def check_api_key():
    key = request.headers.get('X-API-KEY')
    return key == API_KEY

def log_action(action, filename, status):
    extension = os.path.splitext(filename)[1].lstrip('.')
    client_ip = request.remote_addr
    log_entry = LogEntry(
        action=action,
        filename=filename,
        extension=extension,
        client_ip=client_ip,
        status=status
    )
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
            abort(403, description=f"Access Denied: IP {request.remote_addr} not allowed.")
        if not check_api_key():
            abort(401, description="Unauthorized: Invalid API Key")

@app.route('/')
def index():
    files = []
    error = request.args.get('error', '')
    for filename in os.listdir(UPLOAD_FOLDER):
        try:
            files.append(get_file_info(filename))
        except Exception:
            continue
    file_count = len(files)
    allowed_list = ", ".join(ALLOWED_EXTENSIONS)
    return render_template('index.html', files=files, file_count=file_count, api_key=API_KEY, error=error, allowed_list=allowed_list)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        log_action('Upload-Attempt', 'No-File', 'Failed-NoFileSelected')
        return redirect(url_for('index', error="No file selected for upload."))

    file = request.files['image']
    if file.filename == '':
        log_action('Upload-Attempt', 'EmptyFilename', 'Failed-NoFilename')
        return redirect(url_for('index', error="No filename provided."))

    filename = secure_filename(file.filename)
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        allowed_types = ", ".join(ALLOWED_EXTENSIONS)
        log_action('Upload-Attempt', filename, f'Failed-InvalidFileType: {extension}')
        return redirect(url_for('index', error=f"Invalid file type: '{extension}'. Allowed types: {allowed_types}"))

    file.save(os.path.join(UPLOAD_FOLDER, filename))
    log_action('Upload', filename, 'Success')
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    filename = request.form.get('filename')
    if not filename:
        log_action('Delete-Attempt', 'MissingFilename', 'Failed-NoFilenameProvided')
        return jsonify({'status': 'fail', 'message': 'Filename required'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        log_action('Delete', filename, 'Success')
        return jsonify({'status': 'success', 'message': f'File {filename} deleted.'})
    else:
        log_action('Delete-Attempt', filename, 'Failed-FileNotFound')
        return jsonify({'status': 'fail', 'message': f'File {filename} not found.'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
