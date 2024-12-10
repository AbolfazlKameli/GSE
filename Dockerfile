FROM docker.arvancloud.ir/python:3.11.5-slim

LABEL maintainer="abolfazlkameli0@gmail.com"

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app/
CMD ["sh", "-c", "python manage.py migrate"]
