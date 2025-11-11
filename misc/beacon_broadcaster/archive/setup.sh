#!/bin/bash
# Setup script for WiFi Beacon Broadcaster

echo "========================================"
echo "WiFi Beacon Broadcaster Setup"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "[!] Please run setup WITHOUT sudo"
    echo "[!] Run: ./setup.sh"
    exit 1
fi

# Check Python version
echo "[*] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[+] Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "[!] pip3 not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install required system packages
echo ""
echo "[*] Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    iw \
    wireless-tools \
    net-tools \
    python3-dev \
    libpcap-dev

# Install Python requirements
echo ""
echo "[*] Installing Python packages..."
pip3 install -r requirements.txt --user

# Make scripts executable
echo ""
echo "[*] Making scripts executable..."
chmod +x beacon_broadcast.py
chmod +x test_setup.sh
chmod +x cleanup.sh

# Check wireless interface
echo ""
echo "[*] Detecting wireless interfaces..."
iw dev | grep Interface | awk '{print "[+] Found: " $2}'

echo ""
echo "========================================"
echo "[+] Setup Complete!"
echo "========================================"
echo ""
echo "Quick Start:"
echo "  sudo python3 beacon_broadcast.py -s \"TestNetwork\""
echo ""
echo "Test setup:"
echo "  ./test_setup.sh"
echo ""
echo "See README.md for more information"
