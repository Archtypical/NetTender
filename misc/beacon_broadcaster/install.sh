#!/bin/bash
# Sniffy Tester Installation Script

# ANSI color codes
RED='\033[1;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo ""
echo ""
echo -e "${RED}${BOLD}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║                        INSTALLATION WARNING                            ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${YELLOW}${BOLD}║  THIS SCRIPT WILL MODIFY YOUR SYSTEM:                                  ║${NC}"
echo -e "${YELLOW}${BOLD}║                                                                        ║${NC}"
echo -e "${YELLOW}${BOLD}║  SYSTEM-WIDE CHANGES:                                                  ║${NC}"
echo -e "${YELLOW}${BOLD}║    • Installs Python packages with SUDO (scapy, pyserial)              ║${NC}"
echo -e "${YELLOW}${BOLD}║    • Installs system packages (iw, wireless-tools, libpcap-dev)        ║${NC}"
echo -e "${YELLOW}${BOLD}║    • Modifies system Python environment                                ║${NC}"
echo -e "${YELLOW}${BOLD}║                                                                        ║${NC}"
echo -e "${YELLOW}${BOLD}║  POTENTIAL RISKS IF MODIFIED:                                          ║${NC}"
echo -e "${YELLOW}${BOLD}║    • Can break existing Python installations                           ║${NC}"
echo -e "${YELLOW}${BOLD}║    • May conflict with package managers (pip, dnf, apt)                ║${NC}"
echo -e "${YELLOW}${BOLD}║    • Could install malicious packages if script is modified            ║${NC}"
echo -e "${YELLOW}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║  DO NOT MODIFY THIS SCRIPT UNLESS YOU KNOW WHAT YOU'RE DOING           ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}║  IF IT BREAKS YOUR SYSTEM: DON'T COME CRYING TO US!                    ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${YELLOW}${BOLD}║  Review the script before running. You have been warned.               ║${NC}"
echo -e "${RED}${BOLD}║                                                                        ║${NC}"
echo -e "${RED}${BOLD}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
sleep 2

echo "========================================"
echo "Sniffy Tester - Installation"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "[!] Don't run with sudo"
    echo "[!] Run: ./install.sh"
    echo "[!] (Script will prompt for sudo when needed)"
    exit 1
fi

# Check Python
echo "[1/4] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  [✓] Python $PYTHON_VER"
else
    echo "  [✗] Python 3 not found"
    exit 1
fi

# Install system packages
echo ""
echo "[2/4] Installing system dependencies..."
echo "  (This will prompt for sudo password)"

if command -v dnf &> /dev/null; then
    # Fedora/RHEL
    sudo dnf install -y iw wireless-tools python3-devel libpcap-devel
elif command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    sudo apt-get install -y iw wireless-tools python3-dev libpcap-dev
else
    echo "  [!] Unknown package manager - install manually:"
    echo "      iw, wireless-tools, python3-dev, libpcap-dev"
fi

# Install Python packages (system-wide for sudo access)
echo ""
echo "[3/4] Installing Python packages..."
echo "  Installing scapy and pyserial system-wide..."
sudo python3 -m pip install scapy pyserial

# Verify installation
echo ""
echo "[4/4] Verifying installation..."

if sudo python3 -c "import scapy; import serial" 2>/dev/null; then
    echo "  [✓] scapy installed"
    echo "  [✓] pyserial installed"
else
    echo "  [✗] Package installation failed"
    exit 1
fi

# Check wireless interface
echo ""
echo "Detecting wireless interfaces..."
IFACE=$(iw dev 2>/dev/null | grep Interface | head -1 | awk '{print $2}')
if [ -n "$IFACE" ]; then
    echo "  [✓] Found: $IFACE"
else
    echo "  [!] No wireless interface detected"
fi

# Make scripts executable
echo ""
echo "Setting permissions..."
chmod +x monitor_mode.sh sniffy_tester.py

echo ""
echo "========================================"
echo "[✓] Installation Complete!"
echo "========================================"
echo ""
echo "Quick Start:"
echo ""
echo "  1. Create virtual monitor interface (WiFi stays connected!):"
echo "     sudo ./monitor_mode.sh $IFACE setup"
echo ""
echo "  2. Run Sniffy Tester (note: use virtual interface '${IFACE}mon'):"
echo "     sudo python3 sniffy_tester.py -s \"TestAP\" -i ${IFACE}mon"
echo ""
echo "  3. Remove virtual interface when done:"
echo "     sudo ./monitor_mode.sh $IFACE restore"
echo ""
echo "See README.md for more examples!"
echo ""
