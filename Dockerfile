# Dockerfile
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose Flask port
EXPOSE 8080

# Run Flask app
CMD ["python", "app.py"]
