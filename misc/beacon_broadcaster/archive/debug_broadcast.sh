#!/bin/bash
# Debug beacon broadcasting issues

INTERFACE=${1:-wlp0s20f3mon}
CHANNEL=${2:-6}

echo "========================================"
echo "Beacon Broadcast Debugger"
echo "========================================"
echo ""

echo "[*] Interface Information:"
iw dev "$INTERFACE" info 2>/dev/null || iw dev "${INTERFACE%mon}" info
echo ""

echo "[*] Setting interface to 2.4GHz channel $CHANNEL..."
sudo iw dev "$INTERFACE" set channel $CHANNEL 2>/dev/null || \
sudo iw dev "${INTERFACE%mon}" set channel $CHANNEL
echo ""

echo "[*] Verifying channel..."
CURRENT_CHAN=$(iw dev "$INTERFACE" info 2>/dev/null | grep channel | awk '{print $2}')
if [ -z "$CURRENT_CHAN" ]; then
    CURRENT_CHAN=$(iw dev "${INTERFACE%mon}" info 2>/dev/null | grep channel | awk '{print $2}')
fi

echo "Current channel: $CURRENT_CHAN"
echo ""

if [ "$CURRENT_CHAN" = "$CHANNEL" ]; then
    echo "[+] Channel set correctly!"
elif [ "$CURRENT_CHAN" -gt 14 ]; then
    echo "[!] WARNING: Interface is on 5GHz channel $CURRENT_CHAN"
    echo "[!] ESP32 ONLY SUPPORTS 2.4GHz (channels 1-14)!"
    echo "[!] This is why ESP32 can't detect your beacons!"
else
    echo "[?] Channel may not have changed"
fi

echo ""
echo "ESP32 Support:"
echo "  ✓ 2.4GHz: Channels 1-14"
echo "  ✗ 5GHz:   NOT SUPPORTED"
echo ""

echo "Quick Test:"
echo "  sudo iw dev $INTERFACE set channel $CHANNEL"
echo "  sudo python3 integrated_test.py -s \"TestAP\" -c $CHANNEL"
