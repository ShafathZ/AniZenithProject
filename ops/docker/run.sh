#!/bin/bash

docker run -d -p 7002:7002 --name anizenith-container --env-file .env surigo/anizenith:latest


docker compose -f ./ops/docker/compose.yml down
docker compose -f ./ops/docker/compose.yml pull
docker compose -f ./ops/docker/compose.yml up -d