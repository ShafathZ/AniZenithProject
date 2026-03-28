docker build -t surigo/anizenith_backend:latest -f ./docker/backend.dockerfile --progress=plain --no-cache . 
docker build -t surigo/anizenith_frontend:latest -f ./docker/frontend.dockerfile --progress=plain --no-cache .
# docker push surigo/anizenith_backend:latest
# docker push surigo/anizenith_frontend:latest