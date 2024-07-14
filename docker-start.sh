#!/bin/sh
set -ex

echo "downloading docker images"
docker-compose pull
echo "starting docker containers"
docker-compose up -d