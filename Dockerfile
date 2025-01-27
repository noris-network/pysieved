FROM python:3.11

RUN apt-get update && \
  apt-get install --no-install-recommends -y \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    build-essential \
    python3-setuptools \
    debhelper \
    devscripts \
    fakeroot \
    dh-python \
    dh-virtualenv \
    dh-exec && \
  rm -rf /var/lib/apt/lists/*

ADD . / /root/pysieved/

WORKDIR /root/pysieved/
