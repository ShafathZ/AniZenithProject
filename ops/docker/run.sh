#!/bin/bash
docker compose -f ./ops/docker/compose.yml down
docker compose -f ./ops/docker/compose.yml pull
docker compose -f ./ops/docker/compose.yml up -d