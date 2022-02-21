# syntax=docker/dockerfile:1
FROM python:3-alpine
RUN pip install --no-cache-dir pymemcache pika dnspython Flask Flask-Session 
WORKDIR /app
COPY frontend .
COPY util .
EXPOSE 15000
CMD ["python3", "frontend.py"]
