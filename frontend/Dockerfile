# Start from the base python:3.12.3-slim which also has debian:12-slim as base layer
FROM python:3.12.3-slim

# Copy frontend files and folders
# This creates a new folder called "/anizenith_frontend/frontend" and pastes contents of "frontend" folder into it
COPY frontend/ /anizenith_frontend/frontend

# Copy common folder
# This creates a new folder called "/anizenith_frontend/common" and pastes contents of "common" folder into it
COPY common/ /anizenith_frontend/common

# Set the working directory to /anizenith_frontend folder
WORKDIR /anizenith_frontend

# Install libraries using requirements.txt
RUN pip install -r frontend/requirements.txt --no-cache-dir

# Expose ports
# Frontend app port
EXPOSE 7002

# Start the frontend app once the container is running
CMD ["python", "-m" ,"frontend.app"]
