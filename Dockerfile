FROM debian:bookworm

RUN apt-get update && \
  apt-get install --no-install-recommends -y \
    build-essential \
    devscripts \
    python3-all \
    python3-setuptools \
    debhelper-compat \
    dh-python \
    dh-exec && \
  rm -rf /var/lib/apt/lists/*

ADD . / /root/pysieved/

WORKDIR /root/pysieved/
