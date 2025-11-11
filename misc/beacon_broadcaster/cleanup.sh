#!/bin/bash
# Comprehensive Cleanup Script for Sniffy Tester
# Removes virtual interfaces, stops processes, and cleans up system modifications

# ANSI color codes
RED='\033[1;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear
echo ""
echo -e "${RED}${BOLD}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║                        DANGER ZONE                                     ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║  THIS SCRIPT MANIPULATES SYSTEM NETWORK INTERFACES                     ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║  IF MODIFIED INCORRECTLY, IT CAN:                                      ║${NC}"
echo -e "${RED}${BOLD}║    • PERMANENTLY DESTROY NETWORK INTERFACES                            ║${NC}"
echo -e "${RED}${BOLD}║    • BRICK YOUR WIRELESS CARD                                          ║${NC}"
echo -e "${RED}${BOLD}║    • RENDER YOUR SYSTEM UNABLE TO CONNECT TO NETWORKS                  ║${NC}"
echo -e "${RED}${BOLD}║    • REQUIRE SYSTEM REINSTALLATION TO FIX                              ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║  DO NOT MODIFY THIS SCRIPT UNLESS YOU KNOW EXACTLY WHAT YOU'RE DOING   ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║  IF IT BREAKS YOUR SYSTEM: DON'T COME CRYING TO US!                    ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║  You have been warned. Proceed at your own risk.                       ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
sleep 2

echo "========================================"
echo "Sniffy Tester - System Cleanup"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "[!] Must run as root"
    echo "    sudo ./cleanup.sh"
    exit 1
fi

echo "[*] This will clean up:"
echo "    - Virtual monitor interfaces"
echo "    - Running beacon broadcaster processes"
echo "    - Python cache files"
echo "    - Temporary files"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "[!] Aborted"
    exit 0
fi

echo ""
echo "Starting cleanup..."
echo ""

# 1. Kill all beacon broadcaster processes
echo "[1/5] Stopping beacon broadcaster processes..."
PIDS=$(pgrep -f "sniffy_tester.py|beacon_broadcast.py|integrated_test.py|flood_test.py")
if [ -n "$PIDS" ]; then
    echo "  Found processes: $PIDS"
    pkill -f "sniffy_tester.py"
    pkill -f "beacon_broadcast.py"
    pkill -f "integrated_test.py"
    pkill -f "flood_test.py"
    echo "  [✓] Processes terminated"
else
    echo "  [*] No processes found"
fi

# 2. Remove VIRTUAL monitor interfaces (ending with 'mon')
echo ""
echo "[2/5] Removing virtual monitor interfaces..."
# Look for interfaces ending with 'mon' to identify virtual monitor interfaces
VIRTUAL_MON_IFACES=$(iw dev 2>/dev/null | grep Interface | awk '{print $2}' | grep 'mon$')

if [ -n "$VIRTUAL_MON_IFACES" ]; then
    for IFACE in $VIRTUAL_MON_IFACES; do
        echo "  Removing virtual interface: $IFACE"
        ip link set "$IFACE" down 2>/dev/null
        iw dev "$IFACE" del 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "    [✓] Removed"
        else
            echo "    [!] Could not remove (may already be gone)"
        fi
    done
else
    echo "  [*] No virtual monitor interfaces found"
fi

# 3. Check for any physical interfaces stuck in monitor mode and restore them
echo ""
echo "[3/5] Checking physical interfaces..."
ALL_IFACES=$(iw dev 2>/dev/null | grep Interface | awk '{print $2}' | grep -v 'mon$')

RESTORED=0
for IFACE in $ALL_IFACES; do
    TYPE=$(iw dev "$IFACE" info 2>/dev/null | grep type | awk '{print $2}')
    if [ "$TYPE" = "monitor" ]; then
        echo "  [!] WARNING: Physical interface $IFACE is in monitor mode"
        echo "      Restoring to managed mode..."
        ip link set "$IFACE" down
        iw dev "$IFACE" set type managed
        ip link set "$IFACE" up
        echo "    [✓] Restored to managed mode"
        RESTORED=1
    fi
done

if [ $RESTORED -eq 0 ]; then
    echo "  [✓] All physical interfaces are in managed mode"
fi

# 4. Restart NetworkManager (only if we had to restore physical interfaces)
echo ""
echo "[4/5] Checking NetworkManager..."
if [ $RESTORED -eq 1 ]; then
    echo "  Restarting NetworkManager..."
    systemctl restart NetworkManager 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "    [✓] NetworkManager restarted"
    fi
else
    echo "  [✓] NetworkManager doesn't need restarting"
fi

# 5. Clean up Python cache
echo ""
echo "[5/5] Cleaning Python cache..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/__pycache__" ]; then
    rm -rf "$SCRIPT_DIR/__pycache__"
    echo "  [✓] Removed __pycache__"
fi

find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null
find "$SCRIPT_DIR" -name "*.pyo" -delete 2>/dev/null
echo "  [✓] Removed .pyc/.pyo files"

echo ""
echo "========================================"
echo "[✓] Cleanup Complete!"
echo "========================================"
echo ""
echo "System status:"
echo ""

# Show current interfaces
echo "Wireless interfaces:"
iw dev 2>/dev/null | grep -E "Interface|type" | sed 's/^/  /'

echo ""
echo "NetworkManager status:"
systemctl is-active NetworkManager 2>/dev/null | sed 's/^/  /'

echo ""
echo "[+] WiFi should now be available for normal use"
echo ""
