#!/bin/bash
# Install dependencies system-wide for root access

echo "Installing beacon broadcaster dependencies..."
echo ""
echo "This will install packages system-wide so they work with sudo."
echo ""

# Install system packages
echo "[1/3] Installing system dependencies..."
sudo dnf install -y iw wireless-tools python3-devel libpcap-devel 2>/dev/null || \
sudo apt-get update && sudo apt-get install -y iw wireless-tools python3-dev libpcap-dev 2>/dev/null || \
echo "    Note: Install iw and wireless-tools manually if needed"

# Install Python packages system-wide
echo ""
echo "[2/3] Installing Python packages system-wide..."
sudo python3 -m pip install scapy pyserial

# Verify installation
echo ""
echo "[3/3] Verifying installation..."
if sudo python3 -c "import scapy; import serial; print('✓ All packages installed successfully')" 2>/dev/null; then
    echo ""
    echo "========================================"
    echo "Installation complete!"
    echo "========================================"
    echo ""
    echo "You can now run:"
    echo "  sudo python3 beacon_broadcast.py -s \"TestAP\""
    echo "  sudo python3 integrated_test.py -s \"TestAP\""
else
    echo ""
    echo "[!] Installation verification failed"
    echo "    Try manually: sudo python3 -m pip install scapy pyserial"
fi
