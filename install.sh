#!/bin/bash
set -e

REPO_URL="https://github.com/iPmartNetwork/Network.git"
INSTALL_DIR="/opt/net-orchestrator"
SERVICE_NAME="net-orchestrator"

# ---------------------------
# Helpers
# ---------------------------
require_root() {
  if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root"
    exit 1
  fi
}

pause() {
  read -rp "Press Enter to continue..."
}

# ---------------------------
# Step 1: Root
# ---------------------------
require_root

echo "🚀 Net-Orchestrator Auto Installer"
pause

# ---------------------------
# Step 2: Install dependencies
# ---------------------------
echo "📦 Installing system dependencies..."
apt update
apt install -y iproute2 iptables nftables curl git python3 python3-pip

echo "📦 Installing python dependencies..."
pip3 install --break-system-packages rich psutil requests

# ---------------------------
# Step 3: Clone repo
# ---------------------------
echo "📁 Installing Net-Orchestrator..."
rm -rf "$INSTALL_DIR"
git clone "$REPO_URL" "$INSTALL_DIR"

cd "$INSTALL_DIR"

# ---------------------------
# Step 4: User input
# ---------------------------
echo "🧭 Server role?"
select ROLE in IRAN FOREIGN; do
  [ -n "$ROLE" ] && break
done

read -rp "🔐 Private IP (example: 10.10.10.1): " PRIVATE_IP

echo "🌍 Enter FOREIGN server IPs (space separated):"
read -rp "> " FOREIGN_IPS

read -rp "🔥 Enable firewall? (y/n) [y]: " FW
FW=${FW:-y}

# ---------------------------
# Step 5: Generate profiles.json
# ---------------------------
echo "📝 Creating profiles.json..."

mkdir -p config

cat > config/profiles.json <<EOF
{
  "role": "$ROLE",
  "network": {
    "private_ip": "$PRIVATE_IP",
    "interface": null
  },
  "foreign_servers": [
$(echo "$FOREIGN_IPS" | tr ' ' '\n' | sed 's/.*/    "&",/' | sed '$ s/,$//')
  ],
  "routing": {
    "mode": "full",
    "table": 100
  },
  "firewall": {
    "enabled": $( [ "$FW" = "y" ] && echo true || echo false )
  }
}
EOF

# ---------------------------
# Step 6: Install systemd service
# ---------------------------
echo "⚙️ Installing systemd service..."

cp systemd/net-orchestrator.service /etc/systemd/system/
systemctl daemon-reexec
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# ---------------------------
# Done
# ---------------------------
echo
echo "✅ Installation completed successfully!"
echo "🔎 Service status:"
systemctl status "$SERVICE_NAME" --no-pager
