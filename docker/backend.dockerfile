# Start from the base python:3.12.3-slim which also has debian:12-slim as base layer
FROM python:3.12.3-slim

# Copy backend files and folders
# This creates a new folder called "/anizenith_backend/backend" and pastes contents of "backend" folder into it
COPY backend/ /anizenith_backend/backend

# Copy data files 
# This creates a new folder called "/anizenith_backend/data" and pastes contents of "data" folder into it
COPY data/ /anizenith_backend/data

# TODO: Add COPY for Prometheus Folder

# Set the working directory to /anizenith_backend folder
WORKDIR /anizenith_backend

# Install libraries using requirements.txt
RUN pip install -r backend/requirements.txt

# Expose ports
# Backend app port
EXPOSE 9002

# TODO: Add Prometheus Port for Backend app

# Start the Backend app once the container is running
CMD ["python", "backend/app.py"]
