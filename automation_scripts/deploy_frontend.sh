#!/bin/bash
set -euo pipefail

# Start timer
START_TIME=$(date +%s)

# ┌───────────────────────────────────────────────┐
# │              SETUP VARIABLES                  │
# └───────────────────────────────────────────────┘
PRODUCTION_BRANCH="main"
FRONTEND_PORT=22000
FRONTEND_HOST="paffenroth-23.dyn.wpi.edu"
FRONTEND_USER="group02"
FRONTEND_SSH_KEY="./ssh_keys/group_key"
FRONTEND_ROOT_FOLDER="anizenith_frontend"

# ┌───────────────────────────────────────────────┐
# │           PARSE COMMAND LINE ARGS             │
# └───────────────────────────────────────────────┘
# Loop through each command line option
# first ':' performs silent error handling mode
# 'b' without a colon means it acts as a boolean flag (no argument required)
while getopts ":b" opt; do

  # Start a Switch Case block
  case "$opt" in

    # If option '-b' is provided, detect the current git branch
    b) 
      PRODUCTION_BRANCH=$(git branch --show-current)
      
      # Safety check in case the command fails (e.g., empty repository or detached HEAD)
      if [[ -z "$PRODUCTION_BRANCH" ]]; then
          echo "Error: Could not detect current git branch. Are you in a valid git repository?" >&2
          exit 1
      fi
      ;;

    # Handle unknown options
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;

  esac
done

# Remove parsed options from $@, and leave only non-option positional args
shift $((OPTIND - 1))

echo "Using branch: $PRODUCTION_BRANCH"


# Check if we are in the root directory (check for the ssh_keys folder)
find_out="$(find . -type d -name "ssh_keys")"
if [[ -z "$find_out" ]]; then
    echo "Error: ssh_keys folder not found in the current directory."
    exit 1
fi

echo "Found ssh_keys: $find_out"


# Build SSH base command and SCP base command
SSH_BASE=(ssh -i "$FRONTEND_SSH_KEY" \
            -p "$FRONTEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$FRONTEND_USER"@"$FRONTEND_HOST")

SCP_BASE=(scp -i "$FRONTEND_SSH_KEY" \
            -P "$FRONTEND_PORT" \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null)


# ┌───────────────────────────────────────────────┐
# │     REFRESH PRODUCTION CODE TO DEPLOY         │
# └───────────────────────────────────────────────┘
# Checkout main, do git pull (to get the latest production code)
git checkout $PRODUCTION_BRANCH && git pull || \
{ echo "Git checkout and pull for production branch($PRODUCTION_BRANCH) failed"; exit 1; }

# ┌───────────────────────────────────────────────┐
# │     1. INSTALL PYTHON & SETUP ROOT FOLDER     │
# └───────────────────────────────────────────────┘
"${SSH_BASE[@]}" "
echo -e '\n=== Setting up Python 3.12 ==='

# If the command python3.12 is not found, then install it
if ! command -v python3.12 &>/dev/null; then 
  sudo apt update
  sudo add-apt-repository ppa:deadsnakes/ppa -y
  sudo apt install python3.12 python3.12-venv -y
else
  echo 'Python 3.12 already installed, skipping...'
fi

# Print the python version to confirm installation
python3.12 --version

# Make the directory for FRONTEND_ROOT_FOLDER
mkdir -p $FRONTEND_ROOT_FOLDER"


# ┌───────────────────────────────────────────────┐
# │     2. STOP EXISTING FRONTNED (IF RUNNING)    │
# └───────────────────────────────────────────────┘
"${SSH_BASE[@]}" "
echo -e '\n=== Stopping existing frontend (if running) ==='

# pkill -f matches against the full command. The [p] is a regex based trick to make sure we do not match the pkill command itself
# If the command fails, print no frontend running
# Finally return true
(pkill -f '[p]ython frontend_app.py' && echo 'Stopped frontend' || echo 'No frontend running, skipping...')
true"




# ┌───────────────────────────────────────────────┐
# │           3. COPY FRONTEND FILES              │
# └───────────────────────────────────────────────┘
# Remove old code but preserve .venv directory (to speed up deployment, when the VM was not restarted entirely)
# find . starts search in the current dir
# - maxdepth 1 makes sure we look only at immediate children and don't recurse into subdirectories
# ! -name '.venv' ! -name '.' excludes .venv folder and the current directory itself from the search
# -exec rm -rf {} + delete evrything found using above filters
"${SSH_BASE[@]}" "echo -e '\n=== Cleaning old code (preserving .venv) ===' && \
 cd $FRONTEND_ROOT_FOLDER && \
 find . -maxdepth 1 ! -name '.venv' ! -name '.' -exec rm -rf {} +"

# Copy frontend files and folders
echo -e "=== Copying frontend files to VM ==="
"${SCP_BASE[@]}" -r static/ templates/ frontend_app.py requirements_frontend.txt \
  "$FRONTEND_USER@$FRONTEND_HOST:~/$FRONTEND_ROOT_FOLDER/"


# ┌───────────────────────────────────────────────┐
# │     4. CREATE VENV & INSTALL DEPENDENCIES     │
# └───────────────────────────────────────────────┘
"${SSH_BASE[@]}" "
echo -e '\n=== Installing dependencies ==='
cd $FRONTEND_ROOT_FOLDER

# If .venv folder doesn't exist
if [ ! -d .venv ]; then
  echo 'Creating new venv...'
  python3.12 -m venv .venv

# Else, reuse the existing .venv
else
  echo 'Reusing existing venv...'
fi

# Activate the .venv and install / upgrade dependencies using requirements_frontend.txt
source .venv/bin/activate
pip install -r requirements_frontend.txt"



# ┌───────────────────────────────────────────────┐
# │              5. START FRONTEND                │
# └───────────────────────────────────────────────┘
"${SSH_BASE[@]}" "
 # Navigate to the FRONTEND_ROOT_FOLDER dir
 # Activate the venv
 echo -e '\n=== Starting frontend ==='
 cd $FRONTEND_ROOT_FOLDER || exit 1
 source .venv/bin/activate || exit 1

 # Run the app using python in background
 # Route stdout and stderr to frontend.logs
 # Route stdin to /dev/null
 nohup python frontend_app.py > frontend.logs 2>&1 < /dev/null & disown

 # Sleep for 2 seconds
 sleep 2

 # Check if the python app is running or not
 if pgrep -f '[p]ython frontend_app.py' >/dev/null; then
   echo \"Frontend started successfully\"
   exit 0
 else
   echo \"ERROR: Frontend failed to start. Logs:\"
   tail -20 ~/$FRONTEND_ROOT_FOLDER/frontend.logs
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