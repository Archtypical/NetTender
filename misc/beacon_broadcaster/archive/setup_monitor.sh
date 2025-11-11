#!/bin/bash
# Setup monitor mode interface with proper error handling

INTERFACE=${1:-wlp0s20f3}
MON_INTERFACE="${INTERFACE}mon"

echo "========================================"
echo "Monitor Mode Setup"
echo "========================================"
echo ""
echo "Interface: $INTERFACE"
echo "Monitor:   $MON_INTERFACE"
echo ""

# Check if already exists
if iw dev | grep -q "$MON_INTERFACE"; then
    echo "[*] Monitor interface $MON_INTERFACE already exists"
    echo "[*] Removing it first..."
    sudo iw dev "$MON_INTERFACE" del
    sleep 1
fi

echo "[*] Attempting to create virtual monitor interface..."
echo ""

# Method 1: Try creating virtual interface (preferred - doesn't break WiFi)
echo "[Method 1] Creating virtual interface..."
if sudo iw dev "$INTERFACE" interface add "$MON_INTERFACE" type monitor 2>&1; then
    echo "[+] Virtual interface created!"
    sudo ip link set "$MON_INTERFACE" up

    if iw dev | grep -q "$MON_INTERFACE"; then
        echo "[+] Monitor interface is UP"
        echo ""
        echo "SUCCESS! Virtual monitor interface created."
        echo "Your WiFi should still be connected."
        echo ""
        iw dev
        exit 0
    fi
fi

echo "[!] Virtual interface creation failed"
echo ""
echo "Common causes:"
echo "  1. Driver doesn't support multiple interfaces"
echo "  2. NetworkManager is interfering"
echo "  3. Firmware limitations"
echo ""
echo "========================================"
echo "Alternative Method: Direct Monitor Mode"
echo "========================================"
echo ""
echo "WARNING: This will DISCONNECT your WiFi!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

echo ""
echo "[Method 2] Switching main interface to monitor mode..."
echo ""

# Stop NetworkManager
echo "[*] Stopping NetworkManager..."
sudo systemctl stop NetworkManager

# Kill interfering processes
echo "[*] Killing interfering processes..."
sudo pkill wpa_supplicant 2>/dev/null
sudo pkill dhclient 2>/dev/null

# Switch to monitor mode
echo "[*] Switching $INTERFACE to monitor mode..."
sudo ip link set "$INTERFACE" down
sudo iw dev "$INTERFACE" set type monitor
sudo ip link set "$INTERFACE" up

if iw dev "$INTERFACE" info | grep -q "type monitor"; then
    echo ""
    echo "[+] SUCCESS! $INTERFACE is now in monitor mode"
    echo ""
    echo "To restore your WiFi later, run:"
    echo "  sudo ./restore_wifi.sh"
    echo ""
    iw dev "$INTERFACE" info
else
    echo ""
    echo "[!] Failed to set monitor mode"
    echo "[!] Restoring managed mode..."
    sudo ip link set "$INTERFACE" down
    sudo iw dev "$INTERFACE" set type managed
    sudo ip link set "$INTERFACE" up
    sudo systemctl start NetworkManager
    echo "[!] NetworkManager restarted"
fi
