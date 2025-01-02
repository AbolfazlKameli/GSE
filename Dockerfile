FROM docker.arvancloud.ir/python:3.11.5-slim

LABEL maintainer="abolfazlkameli0@gmail.com"

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
