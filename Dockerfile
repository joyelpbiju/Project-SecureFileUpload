# Dockerfile
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy project files
COPY . .

