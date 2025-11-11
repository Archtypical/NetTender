#!/bin/bash
# Monitor Mode Manager for Sniffy Tester
# Handles setup and teardown of monitor mode

# ANSI color codes
RED='\033[1;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTERFACE="${1}"
ACTION="${2:-setup}"  # setup or restore

show_warning() {
    echo ""
    echo ""
    echo ""
    echo -e "${RED}${BOLD}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}${BOLD}║                                                                        ║${NC}"
    echo -e "${RED}${BOLD}║                     MONITOR MODE WARNING                               ║${NC}"
    echo -e "${RED}${BOLD}║                                                                        ║${NC}"
    echo -e "${YELLOW}${BOLD}║  THIS SCRIPT MANIPULATES YOUR WIRELESS INTERFACE:                      ║${NC}"
    echo -e "${YELLOW}${BOLD}║                                                                        ║${NC}"
    echo -e "${YELLOW}${BOLD}║  WHAT IT DOES:                                                         ║${NC}"
    echo -e "${YELLOW}${BOLD}║    • Stops NetworkManager (disconnects WiFi)                           ║${NC}"
    echo -e "${YELLOW}${BOLD}║    • Switches wireless card to monitor mode                            ║${NC}"
    echo -e "${YELLOW}${BOLD}║    • Kills interfering processes (wpa_supplicant, dhclient)            ║${NC}"
    echo -e "${YELLOW}${BOLD}║                                                                        ║${NC}"
    echo -e "${YELLOW}${BOLD}║  POTENTIAL RISKS IF MODIFIED:                                          ║${NC}"
    echo -e "${YELLOW}${BOLD}║    • Can permanently damage wireless interface                         ║${NC}"
    echo -e "${YELLOW}${BOLD}║    • May prevent reconnection to WiFi networks                         ║${NC}"
    echo -e "${YELLOW}${BOLD}║    • Could require system reboot to recover                            ║${NC}"
    echo -e "${YELLOW}${BOLD}║                                                                        ║${NC}"
    echo -e "${RED}${BOLD}║  DO NOT MODIFY THIS SCRIPT UNLESS YOU KNOW WHAT YOU'RE DOING           ║${NC}"
    echo -e "${RED}${BOLD}║                                                                        ║${NC}"
    echo -e "${RED}${BOLD}║  IF IT BREAKS YOUR WIRELESS: DON'T COME CRYING TO US!                  ║${NC}"
    echo -e "${RED}${BOLD}║                                                                        ║${NC}"
    echo -e "${RED}${BOLD}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    sleep 2
}

usage() {
    echo "Usage: $0 <interface> [setup|restore]"
    echo ""
    echo "Examples:"
    echo "  $0 wlp0s20f3 setup     # Enable monitor mode"
    echo "  $0 wlp0s20f3 restore   # Restore managed mode"
    echo ""
    echo "Find your interface: iw dev"
    exit 1
}

if [ -z "$INTERFACE" ]; then
    usage
fi

if [ "$EUID" -ne 0 ]; then
    echo "[!] Must run as root"
    echo "    sudo $0 $INTERFACE $ACTION"
    exit 1
fi

setup_monitor() {
    echo "========================================"
    echo "Creating virtual monitor interface"
    echo "========================================"
    echo ""
    echo "[*] This creates a VIRTUAL monitor interface"
    echo "[*] Your WiFi will stay connected!"
    echo ""

    # Check if physical interface exists
    if ! iw dev "$INTERFACE" info &>/dev/null; then
        echo "[!] ERROR: Interface $INTERFACE not found"
        exit 1
    fi

    # Define virtual interface name
    MON_INTERFACE="${INTERFACE}mon"

    # Check if virtual interface already exists
    if iw dev "$MON_INTERFACE" info &>/dev/null; then
        echo "[!] Virtual interface $MON_INTERFACE already exists"
        echo "[*] To remove it first, run: sudo $0 $INTERFACE restore"
        exit 1
    fi

    # Create virtual monitor interface
    echo "[*] Creating virtual monitor interface: $MON_INTERFACE"
    iw dev "$INTERFACE" interface add "$MON_INTERFACE" type monitor

    if [ $? -ne 0 ]; then
        echo "[!] FAILED to create virtual interface"
        echo "[!] Your wireless driver may not support virtual interfaces"
        exit 1
    fi

    # Bring up the virtual interface
    echo "[*] Bringing up $MON_INTERFACE..."
    ip link set "$MON_INTERFACE" up

    if [ $? -ne 0 ]; then
        echo "[!] FAILED to bring up interface"
        iw dev "$MON_INTERFACE" del 2>/dev/null
        exit 1
    fi

    # Tell NetworkManager to ignore the monitor interface
    echo "[*] Configuring NetworkManager to ignore monitor interface..."
    nmcli device set "$MON_INTERFACE" managed no 2>/dev/null

    # Verify
    if iw dev "$MON_INTERFACE" info | grep -q "type monitor"; then
        echo ""
        echo "[+] SUCCESS! Virtual monitor interface created"
        echo ""
        echo "Virtual Monitor Interface:"
        iw dev "$MON_INTERFACE" info | grep -E "Interface|addr|type" | sed 's/^/  /'
        echo ""
        echo "Physical Interface (still connected):"
        iw dev "$INTERFACE" info | grep -E "Interface|addr|type|ssid" | sed 's/^/  /'
        echo ""
        echo "Now run:"
        echo "  sudo python3 sniffy_tester.py -s \"TestAP\" -i $MON_INTERFACE"
        echo ""
        echo "To remove virtual interface later:"
        echo "  sudo $0 $INTERFACE restore"
    else
        echo ""
        echo "[!] FAILED to create monitor mode interface"
        iw dev "$MON_INTERFACE" del 2>/dev/null
        exit 1
    fi
}

restore_managed() {
    echo "========================================"
    echo "Removing virtual monitor interface"
    echo "========================================"
    echo ""

    # Define virtual interface name
    MON_INTERFACE="${INTERFACE}mon"

    # Check if virtual interface exists
    if ! iw dev "$MON_INTERFACE" info &>/dev/null; then
        echo "[*] Virtual interface $MON_INTERFACE doesn't exist"
        echo "[*] Nothing to clean up"
        exit 0
    fi

    # Bring down the virtual interface
    echo "[*] Bringing down $MON_INTERFACE..."
    ip link set "$MON_INTERFACE" down 2>/dev/null

    # Delete the virtual interface
    echo "[*] Deleting virtual interface: $MON_INTERFACE"
    iw dev "$MON_INTERFACE" del

    if [ $? -eq 0 ]; then
        echo ""
        echo "[+] Virtual monitor interface removed!"
        echo ""
        echo "Physical Interface Status:"
        iw dev "$INTERFACE" info | grep -E "Interface|addr|type|ssid" | sed 's/^/  /'
        echo ""
        echo "[+] Your WiFi connection is unaffected"
    else
        echo ""
        echo "[!] FAILED to remove virtual interface"
        echo "[!] You may need to reboot"
        exit 1
    fi
}

case "$ACTION" in
    setup)
        show_warning
        setup_monitor
        ;;
    restore)
        restore_managed
        ;;
    *)
        echo "[!] Invalid action: $ACTION"
        usage
        ;;
esac
