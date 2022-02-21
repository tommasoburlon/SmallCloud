# syntax=docker/dockerfile:1
FROM python:3-alpine
RUN pip install --no-cache-dir pymemcache pika dnspython mysql-connector-python
WORKDIR /app
COPY backend .
COPY util .
CMD ["python3", "backend.py"]
