# syntax=docker/dockerfile:1
FROM mysql:5.6
WORKDIR /app
ENV MYSQL_ROOT_PASSWORD="password"
COPY sql/db.sql /docker-entrypoint-initdb.d/db.sql
