# Start from the base python:3.12.3-slim which also has debian:12-slim as base layer
FROM python:3.12.3-slim

# Install curl for container health checks and service diagnostics
RUN apt-get update && apt-get install -y curl

# Copy backend files and folders
# This creates a new folder called "/anizenith/backend" and pastes contents of "backend" folder into it
COPY backend/ /anizenith/backend

# Copy frontend files and folders
# This creates a new folder called "/anizenith/frontend" and pastes contents of "frontend" folder into it
COPY frontend/ /anizenith/frontend

# Copy data files 
# This creates a new folder called "/anizenith/data" and pastes contents of "data" folder into it
COPY data/ /anizenith/data

# Copy common folder
# This creates a new folder called "/anizenith/common" and pastes contents of "common" folder into it
COPY common/ /anizenith/common

# Copy integrated-requirements.txt
COPY integrated-requirements.txt /anizenith

# Set the working directory to /anizenith_backend folder
WORKDIR /anizenith

# Install libraries using requirements.txt
# We need --extra-index-url to tell pip to install the cpu variant of the torch library, as our hardward only has CPU
# --extra-index-url is required as the cpu variant of the torch library is not on the default PyPi artifactory
RUN pip install --upgrade pip
RUN pip install -r integrated-requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Expose ports
# Frontend app port
EXPOSE 7002

# Start the Backend app and the Frontend app once the container is running
# Breakdown of the command:
# CMD ["sh","-c", "..."] executes the string as a command in the 'sh' shell.
# python -u -m [app] 2>&1 runs the app with unbuffered output (-u) and redirects stderr to stdout (2>&1).
# | sed -u 's/^/[app] /' pipes the log output into sed (stream editor, unbuffered with -u).
#   - The pattern s/^/[app] / acts as a substitute command (s).
#   - ^ is a regex anchor that matches the beginning of each log line.
#   - This effectively inserts the tag [app] at the start of every line for easy identification.
# & runs each app's command block in the background.
# wait pauses the shell script, keeping the container alive until all background jobs finish.
CMD ["sh","-c", "( python -u -m frontend.app 2>&1 | sed -u 's/^/[frontend] /' ) & ( python -u -m backend.app 2>&1 | sed -u 's/^/[backend] /' ) & wait" ]