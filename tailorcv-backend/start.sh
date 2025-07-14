#!/bin/bash
# Redirect all output (stdout and stderr) to the console
exec > >(tee /dev/tty) 2>&1

# =================================================================
# Production Startup Script for TailorCV Backend
# =================================================================
# This script is the entry point for the Docker container.
# It logs debugging information and then starts the Gunicorn server.

# --- 1. Log Debugging Information ---
echo "--- 🚀 Launching TailorCV Backend (v2) ---"
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Current Directory: $(pwd)"
echo "------------------------------------"

echo "--- 📁 Files in Current Directory ---"
ls -la
echo "-----------------------------------"

echo "--- 🌍 Environment Variables ---"
# Print all environment variables provided by the platform
printenv | sort
echo "--------------------------------"

# --- 2. Start the Application ---
echo "--- 🦄 Starting Gunicorn Server ---"
echo "Binding to 0.0.0.0 on PORT: $PORT"

# Execute Gunicorn
# --bind: The socket to bind to.
# --workers: The number of worker processes.
# --timeout: The number of seconds to wait for a request before timing out.
# --log-level=debug: Print detailed logs.
# app:app: Look for the 'app' object in the 'app.py' file.
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --log-level=debug \
    app:app 