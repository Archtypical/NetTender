#!/bin/bash
# Quick test script for ESP32 integration

echo "========================================"
echo "ESP32 + Beacon Broadcaster Test"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "[!] Please run with sudo"
    echo "    sudo ./test_esp32.sh"
    exit 1
fi

# Default values
SSID="ESP32_TEST_AP"
CHANNEL=6
DURATION=30

# Parse arguments
while getopts "s:c:d:p:" opt; do
    case $opt in
        s) SSID="$OPTARG";;
        c) CHANNEL="$OPTARG";;
        d) DURATION="$OPTARG";;
        p) SERIAL_PORT="$OPTARG";;
        *) echo "Usage: $0 [-s SSID] [-c CHANNEL] [-d DURATION] [-p SERIAL_PORT]"
           exit 1;;
    esac
done

echo "[*] Test Configuration:"
echo "    SSID:     $SSID"
echo "    Channel:  $CHANNEL"
echo "    Duration: ${DURATION}s"
if [ -n "$SERIAL_PORT" ]; then
    echo "    Serial:   $SERIAL_PORT"
else
    echo "    Serial:   Auto-detect"
fi
echo ""

# Check for ESP32
echo "[*] Looking for ESP32..."
if [ -n "$SERIAL_PORT" ]; then
    if [ -e "$SERIAL_PORT" ]; then
        echo "[+] Found ESP32 at $SERIAL_PORT"
    else
        echo "[!] ERROR: $SERIAL_PORT not found"
        exit 1
    fi
else
    # Auto-detect
    ESP32_PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
    if [ -z "$ESP32_PORT" ]; then
        echo "[!] WARNING: No ESP32 detected"
        echo "[!] Make sure ESP32 is connected via USB"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "[+] Found ESP32 at $ESP32_PORT"
        SERIAL_PORT="$ESP32_PORT"
    fi
fi

echo ""
echo "[*] Starting integrated test..."
echo "[*] Press Ctrl+C to stop"
echo ""
sleep 2

# Build command
CMD="python3 integrated_test.py -s \"$SSID\" -c $CHANNEL"
if [ -n "$SERIAL_PORT" ]; then
    CMD="$CMD --serial-port $SERIAL_PORT"
fi

# Run for specified duration
echo "[*] Running test for ${DURATION} seconds..."
timeout ${DURATION}s $CMD

echo ""
echo "[+] Test complete!"
echo ""
echo "What to check:"
echo "  1. Did your WiFi stay connected? (it should have!)"
echo "  2. Did ESP32 detect the \"$SSID\" beacon?"
echo "  3. Was the channel $CHANNEL detected?"
echo ""
