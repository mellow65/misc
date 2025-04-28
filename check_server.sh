#!/bin/bash

# Define the server name and the command to start it
SERVER_NAME="Main_Server"
START_COMMAND="bash /opt/pzserver/start-server.sh -servername $SERVER_NAME"

# Check if the server is running
if ! pgrep -f "start-server.sh -servername $SERVER_NAME" > /dev/null; then
    echo "Server is not running. Starting the server..."
    # Start the server in a new tmux session
    tmux new-session -d -s pzserver "$START_COMMAND"
else
    echo "Server is already running."
fi
