#!/bin/bash
set -euo pipefail

# ┌───────────────────────────────────────────────┐
# │              SETUP VARIABLES                  │
# └───────────────────────────────────────────────┘
PRODUCTION_BRANCH="main"
BACKEND_PORT=22002
BACKEND_HOST="paffenroth-23.dyn.wpi.edu"
BACKEND_USER="group02"
BACKEND_SSH_KEY="./ssh_keys/group02_key"
BACKEND_ROOT_FOLDER="anizenith_backend"


# Check if we are in the root directory (check for the ssh_keys folder)
find_out="$(find . -type d -name "ssh_keys")"
if [[ -z "$find_out" ]]; then
    echo "Error: ssh_keys folder not found in the current directory."
    exit 1
fi

echo "Found ssh_keys: $find_out"


# ┌───────────────────────────────────────────────┐
# │     REFRESH PRODUCTION CODE TO DEPLOY         │
# └───────────────────────────────────────────────┘
# Checkout main, do git pull (to get the latest production code)
# TODO: if this fails, kill the script here
git checkout $PRODUCTION_BRANCH && git pull || \
{ echo "Git checkout and pull for production branch($PRODUCTION_BRANCH) failed"; exit 1; }

# Build SSH command
# TODO: Add Timeout Later
SSH_BASE=(ssh -i "$BACKEND_SSH_KEY" \
            -p "$BACKEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$BACKEND_USER"@"$BACKEND_HOST")

SCP_BASE=(scp -i "$BACKEND_SSH_KEY" \
            -P "$BACKEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null)

# echo "${SSH_BASE[@]}"

# 1. SSH into VM
# Install Python 3.12 and venv using apt, 
# Create backend root folder
"${SSH_BASE[@]}" "sudo apt update && \
 sudo add-apt-repository ppa:deadsnakes/ppa -y && \
 sudo apt install python3.12 python3.12-venv -y && \
 python3.12 --version && \
 mkdir -p $BACKEND_ROOT_FOLDER"


# 2 SCP backend end folder and files into the VM
"${SCP_BASE[@]}" -r backend/ app.py requirements.txt \
"$BACKEND_USER@$BACKEND_HOST:~/$BACKEND_ROOT_FOLDER/" 


# 3. Create Venv using requirements.txt
"${SSH_BASE[@]}" "cd $BACKEND_ROOT_FOLDER && \
 python3.12 -m venv .venv && \
 source .venv/bin/activate && \
 pip install -r requirements.txt"


# 4. Activate the Virtual Env, Run the backend app and route its logs to a log file
"${SSH_BASE[@]}" "cd $BACKEND_ROOT_FOLDER && \
 source .venv/bin/activate && \
 nohup python app.py > backend.logs 2>&1 < /dev/null & \
 echo \$! > backend.pid && \
 echo Started backend with PID \$(cat backend.pid)"