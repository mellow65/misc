#!/bin/bash

# List of Proxmox nodes: "hostname_or_ip label"
NODES=(
  "10.0.2.20 proxmox1"
  "10.0.2.21 proxmox2"
)

# Temporary directory
TMP_DIR="/tmp/proxmox_certs"

# Ensure tmp dir exists
mkdir -p "$TMP_DIR"

echo "Fetching and installing Proxmox certificates..."

for NODE in "${NODES[@]}"; do
  read -r HOST LABEL <<< "$NODE"

  echo "🔐 Connecting to $LABEL ($HOST)..."

  # Fetch cert
  scp root@"$HOST":/etc/pve/local/pve-ssl.pem "$TMP_DIR/$LABEL.crt"

  # Move to system CA directory
  sudo cp "$TMP_DIR/$LABEL.crt" /usr/local/share/ca-certificates/"$LABEL".crt
done

echo "🧼 Cleaning up temp files..."
rm -rf "$TMP_DIR"

echo "🔄 Updating system trust store..."
sudo update-ca-certificates

echo "🔁 Restarting Caddy..."
sudo systemctl restart caddy

echo "✅ Done. Certificates from Proxmox nodes are now trusted."
