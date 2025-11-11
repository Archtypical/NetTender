#!/bin/bash
# Test script to verify beacon broadcaster setup

echo "========================================"
echo "Beacon Broadcaster Setup Test"
echo "========================================"
echo ""

PASS=0
FAIL=0

# Test 1: Check Python
echo "[TEST 1] Checking Python 3..."
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version 2>&1)
    echo "  [✓] PASS: $VERSION"
    ((PASS++))
else
    echo "  [✗] FAIL: Python 3 not found"
    ((FAIL++))
fi

# Test 2: Check Scapy
echo "[TEST 2] Checking Scapy installation..."
if python3 -c "import scapy" 2>/dev/null; then
    VERSION=$(python3 -c "import scapy; print(scapy.__version__)" 2>/dev/null)
    echo "  [✓] PASS: Scapy $VERSION installed"
    ((PASS++))
else
    echo "  [✗] FAIL: Scapy not installed"
    echo "      Run: pip3 install scapy"
    ((FAIL++))
fi

# Test 3: Check iw command
echo "[TEST 3] Checking iw (wireless tools)..."
if command -v iw &> /dev/null; then
    echo "  [✓] PASS: iw installed"
    ((PASS++))
else
    echo "  [✗] FAIL: iw not installed"
    echo "      Run: sudo apt-get install iw"
    ((FAIL++))
fi

# Test 4: Check wireless interface
echo "[TEST 4] Checking for wireless interface..."
IFACE=$(iw dev 2>/dev/null | grep Interface | head -1 | awk '{print $2}')
if [ -n "$IFACE" ]; then
    echo "  [✓] PASS: Found interface '$IFACE'"
    ((PASS++))
else
    echo "  [✗] FAIL: No wireless interface detected"
    echo "      Make sure you have a WiFi card"
    ((FAIL++))
fi

# Test 5: Check monitor mode support
if [ -n "$IFACE" ]; then
    echo "[TEST 5] Checking monitor mode support..."
    if iw phy 2>/dev/null | grep -q monitor; then
        echo "  [✓] PASS: Monitor mode supported"
        ((PASS++))
    else
        echo "  [?] WARNING: Monitor mode support unclear"
        echo "      You may still be able to create virtual interfaces"
        ((PASS++))
    fi
else
    echo "[TEST 5] Skipping (no interface)"
    ((FAIL++))
fi

# Test 6: Check root access
echo "[TEST 6] Checking root access availability..."
if sudo -n true 2>/dev/null; then
    echo "  [✓] PASS: Can use sudo without password"
    ((PASS++))
else
    echo "  [?] INFO: Will need password for sudo"
    echo "      This is normal and not a problem"
    ((PASS++))
fi

# Test 7: Check script permissions
echo "[TEST 7] Checking script permissions..."
if [ -x "beacon_broadcast.py" ]; then
    echo "  [✓] PASS: beacon_broadcast.py is executable"
    ((PASS++))
else
    echo "  [!] INFO: Making beacon_broadcast.py executable"
    chmod +x beacon_broadcast.py
    ((PASS++))
fi

echo ""
echo "========================================"
echo "Results: $PASS passed, $FAIL failed"
echo "========================================"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "[✓] All tests passed! Ready to broadcast."
    echo ""
    echo "Try it out:"
    echo "  sudo python3 beacon_broadcast.py -s \"TestAP\""
    exit 0
else
    echo "[!] Some tests failed. Fix the issues above."
    exit 1
fi
