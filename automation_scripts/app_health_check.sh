#!/bin/bash

# Move to script's parent's parent directory (Should be app root directory)
cd "$(dirname "$0")/.."

# Constants
USER="group02"

# Frontend info
FRONTEND_HOST="paffenroth-23.dyn.wpi.edu"
FRONTEND_HTTP_PORT=7002
FRONTEND_SSH_PORT=22000
FRONTEND_SSH_KEY="./ssh_keys/group_key"

# Backend info
BACKEND_HOST="paffenroth-23.dyn.wpi.edu"
BACKEND_HTTP_PORT=9002
BACKEND_SSH_PORT=22002
BACKEND_SSH_KEY="./ssh_keys/group02_key"

TIMEOUT=5

# Tell user health script has started
current_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "-----HEALTH CHECK SCRIPT STARTED AT: $current_time -----"

# Function to check HTTP server via HEAD request
check_http() {
    local host=$1
    local port=$2
    local timeout=$3

    CURL_BASE=(curl -Is --connect-timeout "$timeout" "http://$host:$port")
    echo -e "${CURL_BASE[@]}"

    "${CURL_BASE[@]}" >/dev/null 2>&1
    local status=$?
    if [ $status -eq 0 ]; then
        return 0 # 0 if success
    elif [ $status -eq 28 ]; then
        echo "HTTP check for $host:$port timed out"
        return 2 # 2 if timeout
    else
        echo "HTTP check failed for $host:$port (exit $status)"
        return 1 # 1 for failed but not timed out
    fi
}

# Function to check SSH connectivity
check_ssh() {
    local user=$1
    local host=$2
    local key=$3
    local ssh_port=$4
    local timeout=$5

    # Run ssh inside timeout

    SSH_BASE=(ssh -i "$key" -p "$ssh_port" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$user"@"$host")
    echo -e "${SSH_BASE[@]}"

    timeout "${timeout}s" "${SSH_BASE[@]}"
    local status=$?

    if [ $status -eq 0 ]; then
        return 0 # 0 if success
    elif [ $status -eq 124 ]; then
        echo "SSH check for $user@$host:$ssh_port timed out"
        return 2 # 2 if timeout
    else
        echo "SSH check failed for $user@$host:$ssh_port (exit $status)"
        return 1 # 1 for failed but not timed out
    fi
}

# Function to report status based on HTTP and SSH results
# Adding colors to output so it looks better in bash
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
RESET="\033[0m"
report_status() {
    local name=$1
    local http_ok=$2
    local ssh_ok=$3

    if [ $http_ok -eq 0 ] && [ $ssh_ok -eq 0 ]; then
        echo -e "${GREEN}$name: Server is running${RESET}"
    elif [ $http_ok -eq 2 ] || [ $ssh_ok -eq 2 ]; then
        echo -e "${YELLOW}$name: Server timed out (Make sure you are on correct VPN and connected to internet. If so, server connection may be down)${RESET}"
    elif [ $http_ok -ne 0 ] && [ $ssh_ok -eq 0 ]; then
        echo -e "${RED}$name: Server down | VM accessible (Backend likely crashed)${RESET}"
    elif [ $http_ok -ne 0 ] && [ $ssh_ok -ne 0 ]; then
        echo -e "${RED}$name: Server down | VM inaccessible (VM may have reset)${RESET}"
    elif [ $http_ok -eq 0 ] && [ $ssh_ok -ne 0 ]; then
        echo -e "${RED}$name: Server responds but SSH inaccessible (Server SSH may be misconfigured)${RESET}"
    fi
}

# Check frontend
check_http "$FRONTEND_HOST" "$FRONTEND_HTTP_PORT" "$TIMEOUT"
FRONTEND_HTTP=$?

check_ssh "$USER" "$FRONTEND_HOST" "$FRONTEND_SSH_KEY" "$FRONTEND_SSH_PORT" "$TIMEOUT"
FRONTEND_SSH=$?

report_status "Frontend" $FRONTEND_HTTP $FRONTEND_SSH

# Check backend
check_http "$BACKEND_HOST" "$BACKEND_HTTP_PORT" "$TIMEOUT"
BACKEND_HTTP=$?

check_ssh "$USER" "$BACKEND_HOST" "$BACKEND_SSH_KEY" "$BACKEND_SSH_PORT" "$TIMEOUT"
BACKEND_SSH=$?

report_status "Backend" $BACKEND_HTTP $BACKEND_SSH

echo "-----HEALTH CHECK SCRIPT COMPLETED -----"