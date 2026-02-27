#!/bin/bash
set -euo pipefail

# ┌───────────────────────────────────────────────┐
# │              SETUP VARIABLES                  │
# └───────────────────────────────────────────────┘
PRODUCTION_BRANCH="main"
FRONTEND_PORT=22000
FRONTEND_HOST="paffenroth-23.dyn.wpi.edu"
FRONTEND_USER="group02"
FRONTEND_SSH_KEY="./ssh_keys/group_key"
FRONTEND_ROOT_FOLDER="anizenith_frontend"


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
git checkout $PRODUCTION_BRANCH && git pull || \
{ echo "Git checkout and pull for production branch($PRODUCTION_BRANCH) failed"; exit 1; }

# Build SSH command
# TODO: Add Timeout
SSH_BASE=(ssh -i "$FRONTEND_SSH_KEY" \
            -p "$FRONTEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$FRONTEND_USER"@"$FRONTEND_HOST")

SCP_BASE=(scp -i "$FRONTEND_SSH_KEY" \
            -P "$FRONTEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null)

# echo "${SSH_BASE[@]}"

# 1. Install Python, Pip and Venv using apt, and create frontend root folder
# SSH Into the VM
"${SSH_BASE[@]}" "sudo apt update && \
 sudo add-apt-repository ppa:deadsnakes/ppa -y && \
 sudo apt install python3.12 python3.12-venv -y && \
 python3.12 --version && \
 mkdir -p $FRONTEND_ROOT_FOLDER"


# 2 SCP Front end folder and files into the VM
"${SCP_BASE[@]}" -r static/ templates/ frontend_app.py requirements_frontend.txt \
"$FRONTEND_USER@$FRONTEND_HOST:~/$FRONTEND_ROOT_FOLDER/"

# 3. Create Venv using requirements-frontend.txt
"${SSH_BASE[@]}" "cd $FRONTEND_ROOT_FOLDER && \
 python3.12 -m venv .venv && \
 source .venv/bin/activate && \
 pip install -r requirements_frontend.txt"

# 4. Activate the Virtual Env, Run the frontend app and route its logs to a log file
"${SSH_BASE[@]}" "cd $FRONTEND_ROOT_FOLDER && \
 source .venv/bin/activate && \
 nohup python frontend_app.py > frontend.logs 2>&1 < /dev/null & \
 echo \$! > frontend.pid && \
 echo Started frontend with PID \$(cat frontend.pid)"