#!/bin/bash
set -euo pipefail

# Define constants
USER="group02"
PORT="22002"
SERVER="paffenroth-23.dyn.wpi.edu"
KEY_DIR="../ssh_keys"
COMMON_KEY_PATH="../ssh_keys/group_key"
NEW_KEY_PATH="../ssh_keys/group02_key"
echo -e "Script Variables:\n" "USER: ""$USER\n" "PORT: ""$PORT\n" "SERVER: ""$SERVER\n" "COMMON_KEY_PATH: ""$COMMON_KEY_PATH\n" "NEW_KEY_PATH: ""$NEW_KEY_PATH\n"


# Move to the script's directory
cd "$(dirname "$0")"
echo "Moved to directory" $(pwd)


# Set initial SSH key permissions
chmod 700 "$KEY_DIR"
ls -l "$KEY_DIR"


# Setup SSH command
SSH_BASE=(ssh -i "$COMMON_KEY_PATH" -p "$PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${USER}@${SERVER}")
echo -e "\nSSH BASE COMMAND:\n" "${SSH_BASE[@]}"


# Get Content of New Key
NEW_KEY_CONTENT="$(cat "${NEW_KEY_PATH}.pub")"
echo -e "\nNew Key Content\n" "$NEW_KEY_CONTENT"


# # Replace authorized keys with secure key
"${SSH_BASE[@]}" \
"echo $NEW_KEY_CONTENT > ~/.ssh/authorized_keys"


# Create a new SSH command which uses the new key
SSH_BASE[2]="${NEW_KEY_PATH}"

# Print the new command to use
echo -e "\nSSH BASE COMMAND (NEW_KEY):\n" "${SSH_BASE[@]}"

# Use the new key to login and print the contents of authorized_keys
if ! "${SSH_BASE[@]}" "cat ~/.ssh/authorized_keys"; then
exit 1
fi

# Print Success Message
echo -e "\n\nSuccessfully established ${NEW_KEY_PATH} as the only key to login into ${USER}@${SERVER}"


