# Troubleshooting Guide

## Virtual Interface Creation Failed

If you see `[!] Virtual interface creation failed`, your wireless card may not support multiple virtual interfaces while connected to WiFi.

### Solution 1: Use Direct Monitor Mode (Disconnects WiFi)

**This will disconnect your WiFi temporarily:**

```bash
# Setup monitor mode (will disconnect WiFi!)
sudo ./setup_monitor.sh

# Run beacon broadcaster
sudo python3 beacon_broadcast.py -s "TestAP" -i wlp0s20f3 --no-virtual

# When done, restore WiFi
sudo ./restore_wifi.sh
```

### Solution 2: Use USB WiFi Adapter

The best solution is to use a cheap USB WiFi adapter:

```bash
# Keep your built-in WiFi (wlp0s20f3) connected
# Use USB adapter (wlan1) for monitor mode

# 1. Plug in USB WiFi adapter
# 2. Find it
iw dev

# 3. Use it for monitoring
sudo python3 beacon_broadcast.py -s "TestAP" -i wlan1
```

**Recommended USB WiFi adapters for monitor mode:**
- Alfa AWUS036NHA (Atheros AR9271) - $30
- TP-Link TL-WN722N v1 (NOT v2/v3) - $15
- Panda PAU05 - $15

### Solution 3: Test Without Monitor Mode

For basic testing, you can use `hostapd` to create a real access point:

```bash
# Install hostapd
sudo dnf install hostapd  # Fedora
# or
sudo apt install hostapd  # Ubuntu/Debian

# Create simple config
sudo tee /tmp/hostapd_test.conf > /dev/null << 'EOF'
interface=wlp0s20f3
ssid=TestAP
channel=6
hw_mode=g
EOF

# Run hostapd (will disconnect your WiFi!)
sudo hostapd /tmp/hostapd_test.conf
```

## Common Error Messages

### "Device or resource busy"

**Cause:** NetworkManager is using the interface

**Fix:**
```bash
sudo systemctl stop NetworkManager
sudo ./setup_monitor.sh
```

### "Operation not permitted"

**Cause:** Not running as root

**Fix:**
```bash
sudo python3 beacon_broadcast.py -s "TestAP"
```

### "No such device"

**Cause:** Wrong interface name

**Fix:**
```bash
# Find your interface
iw dev

# Use the correct name
sudo python3 beacon_broadcast.py -s "TestAP" -i wlp0s20f3
```

## Check Your Wireless Card Capabilities

```bash
# See if your card supports monitor mode
iw phy | grep -A 10 "Supported interface modes"

# Should see "monitor" in the list

# Check if virtual interfaces are supported
iw phy | grep -A 20 "interface combinations"

# Look for something like:
#   * #{ managed } <= 1, #{ AP, P2P-client, P2P-GO } <= 1, #{ P2P-device } <= 1
#   total <= 3, #channels <= 1
```

## Intel Wireless Cards (Like Yours)

Intel wireless cards (like your `wlp0s20f3`) sometimes have issues with virtual interfaces when connected.

**Workaround options:**

1. **Disconnect from WiFi first:**
   ```bash
   nmcli dev disconnect wlp0s20f3
   sudo python3 integrated_test.py -s "TestAP"
   # Reconnect after: nmcli dev connect wlp0s20f3
   ```

2. **Use Ethernet for internet, WiFi for testing**

3. **Get a USB WiFi adapter** (best solution)

## Testing Without ESP32

If you don't have your ESP32 connected, use broadcast-only mode:

```bash
# No serial monitoring
sudo python3 integrated_test.py -s "TestAP" --no-serial

# Or use standalone broadcaster
sudo python3 beacon_broadcast.py -s "TestAP"
```

## Verify Monitor Mode Is Working

```bash
# After creating monitor interface, verify it
iw dev

# Should see something like:
# Interface wlp0s20f3mon
#     type monitor

# Try capturing packets
sudo timeout 5s tcpdump -i wlp0s20f3mon -c 10 type mgt subtype beacon

# Should see beacon frames
```

## Still Not Working?

1. **Check kernel version:**
   ```bash
   uname -r
   # Newer kernels have better wireless support
   ```

2. **Update wireless firmware:**
   ```bash
   # Fedora
   sudo dnf update iwl*-firmware

   # Ubuntu/Debian
   sudo apt update && sudo apt upgrade linux-firmware
   ```

3. **Check dmesg for errors:**
   ```bash
   sudo dmesg | grep -i wireless
   sudo dmesg | grep -i iwl
   ```

4. **Try a different channel:**
   ```bash
   # Your card is on 5GHz channel 36
   # Try 2.4GHz channels (1-14)
   sudo python3 beacon_broadcast.py -s "TestAP" -c 6
   ```

## Quick Reference

| Problem | Solution |
|---------|----------|
| Virtual interface fails | Use `./setup_monitor.sh` for direct mode |
| WiFi disconnects | Expected if not using virtual interface |
| Need WiFi while testing | Use USB WiFi adapter |
| Permission denied | Run with `sudo` |
| Wrong interface name | Check with `iw dev` |
| ESP32 not detected | Specify with `--serial-port /dev/ttyACM0` |

## Get Help

If you're still stuck, gather this info:

```bash
# Wireless card info
lspci | grep -i wireless
iw dev
iw phy | grep -A 30 "Supported interface"

# Kernel and driver
uname -r
modinfo iwlwifi 2>/dev/null || modinfo ath9k 2>/dev/null

# Error messages
sudo dmesg | tail -20
```
