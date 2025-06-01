FROM docker.arvancloud.ir/ubuntu:22.04

LABEL maintainer="abolfazlkameli0@gmail.com"

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY ../requirements.txt /app/

RUN apt-get update &&\
    apt-get install python3 python3-pip libmagic-dev libmagic1 ffmpeg -y &&\
    apt-get clean

RUN pip3 install --no-cache-dir -r requirements.txt

COPY .. /app/

RUN chmod +x /app/docker/entrypoint.sh
ENTRYPOINT ["bash", "-c", "/app/docker/entrypoint.sh"]
