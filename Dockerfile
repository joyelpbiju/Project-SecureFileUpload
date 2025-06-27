# Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /app/uploads /app/db

EXPOSE 8084

CMD ["python", "app.py"]
