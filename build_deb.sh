#!/bin/bash

export BUILD_VERSION=0.2.0

docker build -t pysieved-deb-builder .
docker run --name pysieved-builder pysieved-deb-builder dpkg-buildpackage -b -us -uc -rfakeroot -tc
docker cp pysieved-builder:/root/pysieved_${BUILD_VERSION}_amd64.deb pysieved_${BUILD_VERSION}.deb
docker rm -f pysieved-builder

