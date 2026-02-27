#!/bin/bash
set -euo pipefail

# Start timer
START_TIME=$(date +%s)

# ┌───────────────────────────────────────────────┐
# │              SETUP VARIABLES                  │
# └───────────────────────────────────────────────┘
# PRODUCTION_BRANCH="main" # TODO: Uncomment this before merging PR
PRODUCTION_BRANCH="case-study2/deployment-script"
BACKEND_PORT=22002
BACKEND_HOST="paffenroth-23.dyn.wpi.edu"
BACKEND_USER="group02"
BACKEND_SSH_KEY="./ssh_keys/group02_key"
BACKEND_ROOT_FOLDER="anizenith_backend"
BACKEND_HTTP_PORT=9002


# Check if we are in the root directory (check for the ssh_keys folder)
find_out="$(find . -type d -name "ssh_keys")"
if [[ -z "$find_out" ]]; then
    echo "Error: ssh_keys folder not found in the current directory."
    exit 1
fi

echo "Found ssh_keys: $find_out"


# Build SSH base command and SCP base command
# without -T, SSH to allocates a pseudo-terminal (PTY)
# without -T, when we run uvicorn later, the PTY stays open
# for as long as any process (when we run uvicorn) holds its file descriptors
SSH_BASE=(ssh -T -i "$BACKEND_SSH_KEY" \
            -p "$BACKEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$BACKEND_USER"@"$BACKEND_HOST")

SCP_BASE=(scp -i "$BACKEND_SSH_KEY" \
            -P "$BACKEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null)



# ┌───────────────────────────────────────────────┐
# │       REFRESH PRODUCTION CODE TO DEPLOY       │
# └───────────────────────────────────────────────┘
# Checkout main, do git pull (to get the latest production code)
git checkout $PRODUCTION_BRANCH && git pull || \
{ echo "Git checkout and pull for production branch($PRODUCTION_BRANCH) failed"; exit 1; }


# ┌───────────────────────────────────────────────┐
# │     1. INSTALL PYTHON & SETUP ROOT FOLDER     │
# └───────────────────────────────────────────────┘

# Install Python 3.12 only if not already installed
# Create backend root folder if it doesn't exist
#
# command -v python3.12 returns 0 if the command is found, 1 otherwise
# &>/dev/null redirects stdout and stderr to null
"${SSH_BASE[@]}" "echo -e '=== Setting up Python 3.12 ===' && \
 if ! command -v python3.12 &>/dev/null; then \
   sudo apt update && \
   sudo add-apt-repository ppa:deadsnakes/ppa -y && \
   sudo apt install python3.12 python3.12-venv -y; \
 else \
   echo 'Python 3.12 already installed, skipping...'; \
 fi && \
 python3.12 --version && \
 mkdir -p $BACKEND_ROOT_FOLDER"



# ┌───────────────────────────────────────────────┐
# │     2. STOP EXISTING BACKEND (IF RUNNING)     │
# └───────────────────────────────────────────────┘
# pkill -f matches against the full command line
# || true prevents set -e from exiting if no process was found
"${SSH_BASE[@]}" "echo -e '=== Stopping existing backend (if running) ===' && \
 (pkill -f '[u]vicorn app:app' && echo 'Stopped backend' || echo 'No backend running, skipping...'); \
 true"


# ┌───────────────────────────────────────────────┐
# │           3. COPY BACKEND FILES               │
# └───────────────────────────────────────────────┘
# Remove old code but preserve .venv directory (to speed up deployment, when the VM was not restarted entirely)
# find . starts search in the current dir
# - maxdepth 1 makes sure we look only at immediate children and don't recurse into subdirectories
# ! -name '.venv' ! -name '.' excludes .venv folder and the current directory itself from the search
# -exec rm -rf {} + delete evrything found using above filters
"${SSH_BASE[@]}" "echo -e '=== Cleaning old code (preserving .venv) ===' && \
 cd $BACKEND_ROOT_FOLDER && \
 find . -maxdepth 1 ! -name '.venv' ! -name '.' -exec rm -rf {} +"

# Copy backend folder, app.py, requirements.txt and .env file
echo "=== Copying backend files to VM ==="
"${SCP_BASE[@]}" -r backend/ app.py requirements.txt .env \
  "$BACKEND_USER@$BACKEND_HOST:~/$BACKEND_ROOT_FOLDER/"


# ┌───────────────────────────────────────────────┐
# │     4. CREATE VENV & INSTALL DEPENDENCIES     │
# └───────────────────────────────────────────────┘
# Create venv only if it doesn't exist
# pip install skips already-installed packages automatically
"${SSH_BASE[@]}" "echo -e '\n=== Installing dependencies ===' && \
 cd $BACKEND_ROOT_FOLDER && \
 if [ ! -d .venv ]; then \
   echo 'Creating new venv...' && \
   python3.12 -m venv .venv; \
 else \
   echo 'Reusing existing venv...'; \
 fi && \
 source .venv/bin/activate && \
 pip install -r requirements.txt"


# ┌───────────────────────────────────────────────┐
# │             5. START BACKEND                  │
# └───────────────────────────────────────────────┘
# nohup makes the command immune to hang ups
# > backend.logs 2>&1 redirects stdout and stderr to the same file
# </dev/null detaches stdin so SSH can exit
# & backgrounds the process, disown detaches it from the shell
# pgrep -f checks if the process is running by matching the full command line

"${SSH_BASE[@]}" "
 # Navigate to the BACKEND_ROOT_FOLDER dir
 # Activate the venv
 echo -e '\n=== Starting backend ==='
 cd $BACKEND_ROOT_FOLDER || exit 1
 source .venv/bin/activate || exit 1

 # Run the app using
 nohup uvicorn app:app --host 0.0.0.0 --port $BACKEND_HTTP_PORT --log-level info > backend.logs 2>&1 </dev/null &
 disown \$! || true

 sleep 2
 if pgrep -f '[u]vicorn app:app' >/dev/null; then
   echo \"Backend started successfully\"
   exit 0
 else
   echo \"ERROR: Backend failed to start. Logs:\"
   tail -20 ~/$BACKEND_ROOT_FOLDER/backend.logs
   exit 1
 fi
"


# ┌───────────────────────────────────────────────┐
# │             DEPLOYMENT COMPLETE               │
# └───────────────────────────────────────────────┘
 # Print total deployment time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo -e "\n=== Deployment complete! Total time: $((ELAPSED / 60))m $((ELAPSED % 60))s ==="