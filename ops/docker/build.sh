#!/bin/bash
docker build -t surigo/anizenith_backend:latest -f ./backend/Dockerfile --progress=plain --no-cache .
docker build -t surigo/anizenith_frontend:latest -f ./frontend/Dockerfile --progress=plain --no-cache .
docker build -t surigo/anizenith:latest -f ./Dockerfile --progress=plain --no-cache .


docker push surigo/anizenith_backend:latest
docker push surigo/anizenith_frontend:latest