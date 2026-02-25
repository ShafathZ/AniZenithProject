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
git checkout $PRODUCTION_BRANCH && git pull

# Build SSH command
# TODO: Add Timeout
SSH_BASE=(ssh -i "$FRONTEND_SSH_KEY" \
            -p "$FRONTEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$FRONTEND_USER"@"$FRONTEND_HOST")

SCP_BASE=(scp -i "$FRONTEND_SSH_KEY" \
            -p "$FRONTEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$FRONTEND_USER"@"$FRONTEND_HOST")

# echo "${SSH_BASE[@]}"

# 1. Install Python, Pip and Venv using apt, and create frontend root folder
# SSH Into the VM
"${SSH_BASE[@]}" "sudo apt update && \
 sudo add-apt-repository ppa:deadsnakes/ppa -y && \
 sudo apt install python3.12 python3.12-venv -y && \
 python3.12 --version && \
 mkdir -p $FRONTEND_ROOT_FOLDER"


# 2 SCP Front end folder and files into the VM
"${SCP_BASE[@]} -r static templates"



# 3. Create Venv using requirements-frontend.txt

# 4. Activate the Virtual Env, Run the frontend app and route its logs to a log file





















































# ┌───────────────────────────────────────────────┐
# │           PROF PAFFENROTH'S EXAMPLE           │
# └───────────────────────────────────────────────┘

# PORT=21003
# MACHINE=paffenroth-23.dyn.wpi.edu
# STUDENT_ADMIN_KEY_PATH=../../scripts/

# # Clean up from previous runs
# ssh-keygen -f "/home/rcpaffenroth/.ssh/known_hosts" -R "[paffenroth-23.dyn.wpi.edu]:21003"
# rm -rf tmp

# # Create a temporary directory
# mkdir tmp

# # copy the key to the temporary directory
# cp ${STUDENT_ADMIN_KEY_PATH}/student-admin_key* tmp

# # Change to the temporary directory
# cd tmp

# # Set the permissions of the key
# chmod 600 student-admin_key*

# # Create a unique key
# rm -f mykey*
# ssh-keygen -f mykey -t ed25519 -N "careful"

# # Insert the key into the authorized_keys file on the server
# # One > creates
# cat mykey.pub > authorized_keys
# # two >> appends
# # Remove to lock down machine
# #cat student-admin_key.pub >> authorized_keys

# chmod 600 authorized_keys

# echo "checking that the authorized_keys file is correct"
# ls -l authorized_keys
# cat authorized_keys

# # Copy the authorized_keys file to the server
# scp -i student-admin_key -P ${PORT} -o StrictHostKeyChecking=no authorized_keys student-admin@${MACHINE}:~/.ssh/

# # Add the key to the ssh-agent
# eval "$(ssh-agent -s)"
# ssh-add mykey

# # Check the key file on the server
# echo "checking that the authorized_keys file is correct"
# ssh -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE} "cat ~/.ssh/authorized_keys"

# # clone the repo
# git clone https://github.com/rcpaffenroth/CS553_example

# # Copy the files to the server
# scp -P ${PORT} -o StrictHostKeyChecking=no -r CS553_example student-admin@${MACHINE}:~/

# # check that the code in installed and start up the product
# # COMMAND="ssh -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}"

# # ${COMMAND} "ls CS553_example"
# # ${COMMAND} "sudo apt install -qq -y python3-venv"
# # ${COMMAND} "cd CS553_example && python3 -m venv venv"
# # ${COMMAND} "cd CS553_example && source venv/bin/activate && pip install -r requirements.txt"
# # ${COMMAND} "nohup CS553_example/venv/bin/python3 CS553_example/app.py > log.txt 2>&1 &"

# # nohup ./whatever > /dev/null 2>&1 

# # debugging ideas
# # sudo apt-get install gh
# # gh auth login
# # requests.exceptions.HTTPError: 429 Client Error: Too Many Requests for url: https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta/v1/chat/completions
# # log.txt