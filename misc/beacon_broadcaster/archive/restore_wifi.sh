#!/bin/bash
# Restore WiFi to normal managed mode

INTERFACE=${1:-wlp0s20f3}
MON_INTERFACE="${INTERFACE}mon"

echo "========================================"
echo "Restoring WiFi"
echo "========================================"
echo ""

# Remove virtual monitor interface if it exists
if iw dev | grep -q "$MON_INTERFACE"; then
    echo "[*] Removing virtual monitor interface..."
    sudo iw dev "$MON_INTERFACE" del
    echo "[+] Removed $MON_INTERFACE"
fi

# Check if main interface is in monitor mode
if iw dev "$INTERFACE" info 2>/dev/null | grep -q "type monitor"; then
    echo "[*] Switching $INTERFACE back to managed mode..."
    sudo ip link set "$INTERFACE" down
    sudo iw dev "$INTERFACE" set type managed
    sudo ip link set "$INTERFACE" up
    echo "[+] Switched to managed mode"
fi

# Restart NetworkManager
echo "[*] Starting NetworkManager..."
sudo systemctl start NetworkManager

sleep 2

echo ""
echo "[+] WiFi restored!"
echo ""
echo "Current status:"
iw dev "$INTERFACE" info 2>/dev/null || echo "Interface not found"
echo ""
echo "You should be able to reconnect to WiFi now."
