#!/bin/bash

set -euo pipefail

BACKEND_HOST="paffenroth-23.dyn.wpi.edu"
BACKEND_SSH_KEY="./ssh_keys/group_key"

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RESET="\033[0m"

# Loop through every group's endpoint using the group SSH key
for GROUP in {1..11}; do
    BACKEND_PORT=$((22000 + GROUP))
    BACKEND_USER=$(printf "group%02d" "$GROUP")

    SSH_BASE=(ssh -i "$BACKEND_SSH_KEY" \
        -p "$BACKEND_PORT" \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        "$BACKEND_USER@$BACKEND_HOST")

    echo "----------------------------------------"
    echo "SSH into group $GROUP using:"
    echo "${SSH_BASE[*]}"
    echo "----------------------------------------"

    # Go to ~/home, list files (To prove we are on the device), and then check in ./ for files to see if they are vulnerable
    SSH_OUTPUT="$("${SSH_BASE[@]}" 'cd ..; echo "LS Output:"; ls -m; echo -e "\nFind Files Output:"; find . -type f ! -path "*/.*" ! -name ".*"' 2>&1 || true)"
    echo "$SSH_OUTPUT"

    FILE_LIST=$(echo "$SSH_OUTPUT" | grep '^./' || true)

    # If the SSH is secured off of public key
    if echo "$SSH_OUTPUT" | grep -q "Permission denied (publickey)"; then
      echo -e "${GREEN}Group $GROUP SSH is secured${RESET}."
    # If there are files found after accessing inside the device (They pushed without securing)
    elif [[ -n "$FILE_LIST" ]]; then
        echo -e "${RED}Red Team Success on Group ${GROUP} with Files:"
        echo "$FILE_LIST! ${RESET}"
    # If we can get in but there is no useful data on the device yet
    else
        echo -e "${YELLOW}Group ${GROUP} SSH is unsecured, but no files found.${RESET}"
    fi

done