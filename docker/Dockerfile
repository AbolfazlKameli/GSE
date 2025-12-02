ARG PYTHON_VERSION=3.13.5

FROM docker.arvancloud.ir/python:${PYTHON_VERSION}-alpine

LABEL maintainer="abolfazlkameli0@gmail.com"

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY ../requirements.txt /app/

RUN apk add --no-cache --virtual .build-deps \
      build-base \
      python3-dev \
      pkgconfig \
      file-dev \
      musl-dev \
      linux-headers \
    && apk add --no-cache \
      libmagic \
      ffmpeg \
    \
    && apk del .build-deps

RUN pip3 install --no-cache-dir -r requirements.txt

COPY .. /app/

RUN chmod +x /app/docker/entrypoint.sh
ENTRYPOINT ["sh", "-c", "/app/docker/entrypoint.sh"]
