FROM docker.arvancloud.ir/python:3.11.5-slim

LABEL maintainer="abolfazlkameli0@gmail.com"

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install libmagic-dev libmagic1 -y && apt-get clean
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["bash", "-c", "/app/entrypoint.sh"]
