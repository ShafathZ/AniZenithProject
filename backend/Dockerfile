# Start from the base python:3.12.3-slim which also has debian:12-slim as base layer
FROM python:3.12.3-slim

# Install curl for container health checks and service diagnostics
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy backend files and folders
# This creates a new folder called "/anizenith_backend/backend" and pastes contents of "backend" folder into it
COPY backend/ /anizenith_backend/backend

# Copy data files 
# This creates a new folder called "/anizenith_backend/data" and pastes contents of "data" folder into it
COPY data/ /anizenith_backend/data

# Copy common folder
# This creates a new folder called "/anizenith_backend/common" and pastes contents of "common" folder into it
COPY common/ /anizenith_backend/common

# Set the working directory to /anizenith_backend folder
WORKDIR /anizenith_backend

# Install libraries using requirements.txt
# We need --extra-index-url to tell pip to install the cpu variant of the torch library, as our hardward only has CPU
# --extra-index-url is required as the cpu variant of the torch library is not on the default PyPi artifactory
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Expose ports
# Backend app port
EXPOSE 9002

# Add Environment Variables
ENV PYTHONPATH=/anizenith_backend

# Start the Backend app once the container is running
CMD ["python", "-m" ,"backend.app"]
