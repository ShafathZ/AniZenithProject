#!/bin/bash
set -euo pipefail

# Start timer
START_TIME=$(date +%s)

# ┌───────────────────────────────────────────────┐
# │              SETUP VARIABLES                  │
# └───────────────────────────────────────────────┘
SSH_PORT=22000
SSH_HOST="paffenroth-23.dyn.wpi.edu"
SSH_USER="group02"
SSH_KEY="./ssh_keys/group02_key"
PROJECT_ROOT_FOLDER="anizenith_deployment"

# Build SSH base command and SCP base command
SSH_BASE=(ssh -i "$SSH_KEY" \
            -p "$SSH_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$SSH_USER"@"$SSH_HOST")

SCP_BASE=(scp -i "$SSH_KEY" \
            -P "$SSH_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null)

# Make the directory for PROJECT_ROOT_FOLDER
"${SSH_BASE[@]}" "
echo -e '\n=== Setup PROJECT ROOT FOLDER ==='
 mkdir -p $PROJECT_ROOT_FOLDER
"

# Remove old files
"${SSH_BASE[@]}" "echo -e '\n=== Cleaning old files ===' && \
 cd $PROJECT_ROOT_FOLDER && \
 rm -rf ./*"

# SCP files to the VM
echo -e "\n=== Copying Deployment Files to VM ==="
"${SCP_BASE[@]}" ./docker/compose.yml ./docker/prometheus.yml ./docker/ngrok.yml ./docker/ngrok.env ./backend/backend.env ./frontend/frontend.env \
  "$SSH_USER@$SSH_HOST:~/$PROJECT_ROOT_FOLDER/"


# Start the containers
"${SSH_BASE[@]}" "
 echo -e '\n=== Pulling Images and Starting up containers ==='
 cd $PROJECT_ROOT_FOLDER

 # Perform docker compose pull, and bring down any existing containers and then spin up all containers again
 docker compose pull
 docker compose down
 docker compose up -d
"


# Print total deployment time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo -e "\n=== Deployment complete! Total time: $((ELAPSED / 60))m $((ELAPSED % 60))s ==="