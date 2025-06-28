# Project-SecureFileUpload
A secure Flask-based web application that allows users to upload and delete images using token-based API authentication. It includes image validation and IP whitelisting to restrict access, ensuring controlled and secure usage.
# Secure File Upload Service

A Flask-based secure image upload and management web application with robust security features including API key authentication, IP restrictions, and comprehensive activity logging.

## 🚀 Features

### Core Functionality
- **Image Upload & Management**: Upload, view, and delete image files through a clean web interface
- **File Type Validation**: Supports multiple image formats (JPG, PNG, GIF, BMP, TIFF, WebP, HEIF, RAW, SVG, PSD)
- **Real-time Preview**: View uploaded images directly in the browser
- **File Information**: Display file size, type, and upload timestamp

### Security Features
- **API Key Authentication**: All upload/delete operations require valid API key
- **IP Address Restrictions**: Configurable whitelist of allowed client IPs
- **Secure File Handling**: Uses werkzeug's `secure_filename()` for safe file naming
- **Input Validation**: Comprehensive validation of file types and requests
- **Activity Logging**: Complete audit trail of all actions stored in SQLite database

### Technical Features
- **SQLite Database**: Persistent logging and data storage
- **Docker Support**: Containerized deployment with docker-compose
- **Environment Configuration**: Secure configuration via environment variables
- **Responsive UI**: Clean, modern web interface with error handling

## 📋 Requirements

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- python-dotenv
- Docker (optional)

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Project-SecureFileUpload
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate API Key**
   ```bash
   python api_key_gen.py
   ```

5. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   API_KEY=your_generated_api_key_here
   UPLOAD_FOLDER=uploads
   ALLOWED_IPS=127.0.0.1,your.allowed.ip.address
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:8084`

### Docker Deployment

1. **Build and run with docker-compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   
   Open `http://localhost:8084` in your browser

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | Authentication key for upload/delete operations | None | Yes |
| `UPLOAD_FOLDER` | Directory for storing uploaded files | `uploads` | No |
| `ALLOWED_IPS` | Comma-separated list of allowed IP addresses | Empty | No |

### Allowed File Types

The application accepts the following image formats:
- **Common**: JPG, JPEG, PNG, GIF, BMP
- **Advanced**: TIFF, WebP, HEIF, RAW, SVG, PSD

## 🔧 Usage

### Web Interface

1. **Access the application** at `http://localhost:8084`
2. **View uploaded files** in the table with file details
3. **Upload new images** using the upload form
4. **Preview images** by clicking the "View" button
5. **Delete files** using the "Delete" button

### API Endpoints

#### Upload File
```http
POST /upload
Content-Type: multipart/form-data
X-API-KEY: your_api_key

Form data:
- image: file (required)
```

#### Delete File
```http
POST /delete
Content-Type: application/x-www-form-urlencoded
X-API-KEY: your_api_key

Form data:
- filename: string (required)
```

#### View File
```http
GET /uploads/{filename}
```

### API Key Management

Generate a new API key:
```bash
python api_key_gen.py
```

This script:
- Generates a secure 32-character random API key
- Updates the `.env` file automatically
- Provides the new key for configuration

## 🗄️ Database Schema

The application uses SQLite to log all activities:

### LogEntry Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| action | String(50) | Action performed (Upload, Delete, etc.) |
| filename | String(200) | Name of the file |
| extension | String(20) | File extension |
| client_ip | String(50) | Client IP address |
| status | String(50) | Operation status |
| timestamp | DateTime | When the action occurred |

## 🐳 Docker Configuration

### Dockerfile
- Based on Python 3.10-slim
- Installs dependencies via pip
- Creates necessary directories
- Exposes port 8084

### docker-compose.yml
- Maps port 8084 to host
- Mounts uploads and database directories
- Loads environment variables from `.env`
- Restarts automatically unless stopped

## 🏗️ Project Structure

```
Project-SecureFileUpload/
├── app.py                 # Main Flask application
├── api_key_gen.py        # API key generation utility
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker Compose setup
├── .env                 # Environment variables (create this)
├── templates/
│   └── index.html       # Web interface template
├── uploads/             # Uploaded files directory
├── db/                  # SQLite database directory
│   └── app.db          # Application database
└── instance/
    └── db/             # Alternative database location
```

## 🔒 Security Considerations

### Current Security Features
- **Authentication**: API key required for modifications
- **Authorization**: IP-based access control
- **Input Validation**: File type and name validation
- **Audit Trail**: Complete logging of all activities
- **Secure Storage**: Files stored outside web root where possible

### Additional Security Recommendations
- Use HTTPS in production
- Implement rate limiting
- Regular API key rotation
- File size limits
- Antivirus scanning for uploads
- Content Security Policy (CSP) headers

## 🚨 Troubleshooting

### Common Issues

1. **403 Forbidden Error**
   - Check if your IP is in the `ALLOWED_IPS` list
   - Verify network configuration

2. **401 Unauthorized Error**
   - Ensure API key is correctly set in `.env`
   - Verify API key is being sent in requests

3. **File Upload Fails**
   - Check file type is supported
   - Verify upload directory permissions
   - Ensure sufficient disk space

4. **Database Issues**
   - Check database directory permissions
   - Verify SQLite installation

### Debug Mode

To enable debug mode, modify `app.py`:
```python
app.run(host='0.0.0.0', port=8084, debug=True)
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review the application logs
- Check Docker container logs: `docker-compose logs`

---

**Note**: This application is designed for internal use with IP restrictions. Ensure proper security measures when deploying to production environments.
