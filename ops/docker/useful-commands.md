# Useful Docker Commands for development
## Commands for building docker images
### Building backend image
```bash
docker build -t surigo/anizenith_backend:latest -f ./backend/Dockerfile --progress=plain --no-cache .
```

### Building frontend image
```bash
docker build -t surigo/anizenith_frontend:latest -f ./frontend/Dockerfile --progress=plain --no-cache .
```

### Building integrated image (backend + frontend)
```bash
docker build -t surigo/anizenith:latest -f ./Dockerfile --progress=plain --no-cache .
```

## Commands for pushing docker images to dockerhub
To push backend and frontend images, use this:
```bash
docker push surigo/anizenith_backend:latest
docker push surigo/anizenith_frontend:latest
```

## Docker compose commands
This module assumes we have a compose.yml file.

### Bring down existing containers
This brings down all existing containers related to services defined within the `compose.yml` file.
```bash
docker compose -f compose.yml down
```

### Pull all required images from DockerHub
This pulls all the required images from DockerHub related to the services defined within the `compose.yml` file.
```bash
docker compose -f compose.yml pull
```

### Spin up all required containers
This spins up all the defined containers as services in the `compose.yml` file.
The `-d` flag ensures that the command runs in background and doesn't occupy the current shell process.
```bash
docker compose -f ./ops/docker/compose.yml up -d
```

## Run command for running the integrated anizenith container
```bash
docker run -d -p 7002:7002 --name anizenith-container --env-file .env surigo/anizenith:latest
```