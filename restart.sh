#!/bin/sh

docker-compose down
docker-compose build
docker-compose up -d
docker logs -f flask_worker