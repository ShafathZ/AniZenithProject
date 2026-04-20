#!/bin/bash
# Commands for building docker images
docker build -t surigo/anizenith_backend:latest -f ./backend/Dockerfile --progress=plain --no-cache .
docker build -t surigo/anizenith_frontend:latest -f ./frontend/Dockerfile --progress=plain --no-cache .
docker build -t surigo/anizenith:latest -f ./Dockerfile --progress=plain --no-cache .

# Commands for pushing docker images to dockerhub
docker push surigo/anizenith_backend:latest
docker push surigo/anizenith_frontend:latest