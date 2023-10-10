# FROM python:3.11.6-bookworm
FROM tiangolo/tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV APP_MODULE app.main:app

# WORKDIR /app

# 한개의 파일만 복사하는 경우
COPY requirements.txt /app/requirements.txt
# 여러개의 파일을 복사하는 경우 /app/을 <dest>로 지정해야 함

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# EXPOSE 80

COPY ./ /app

# CMD ["python", "main.py"]

# tiangolo/uvicorn-gunicorn-fastapi:python3.11
# FROM python:3.11-slim

# LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"

# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir -r /tmp/requirements.txt

# COPY ./start.sh /start.sh
# RUN chmod +x /start.sh

# COPY ./gunicorn_conf.py /gunicorn_conf.py

# COPY ./start-reload.sh /start-reload.sh
# RUN chmod +x /start-reload.sh

# COPY ./app /app
# WORKDIR /app/

# ENV PYTHONPATH=/app

# EXPOSE 80

# # Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# # And then will start Gunicorn with Uvicorn
# CMD ["/start.sh"]