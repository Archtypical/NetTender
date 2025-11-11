# Sniffy Tester

**WiFi beacon broadcaster for testing ESP32 Sniffy war driving device**

A streamlined Python tool that broadcasts WiFi beacon frames to test your ESP32's packet sniffing capabilities. Supports continuous broadcasting, flood mode with unique MACs, and integrated ESP32 serial monitoring.

## Features

✨ **Three Test Modes:**
- **Simple Mode**: Continuous broadcast with single MAC
- **Flood Mode**: Multiple beacons with unique MACs (triggers ESP32 [NEW DEVICE] for each)
- **Integrated Mode**: Broadcast + live ESP32 serial monitoring

📡 **2.4GHz WiFi Support:**
- Channels 1-14
- Custom SSID and MAC address
- Encrypted or open network simulation

🔌 **ESP32 Integration:**
- Auto-detect ESP32 serial port
- Real-time packet detection monitoring
- Statistics display

## Quick Start

### 1. Install (One Time)

```bash
cd /home/user/Projects/esp32/misc/beacon_broadcaster
./install.sh
```

This installs:
- `scapy` - Packet crafting library
- `pyserial` - ESP32 serial communication
- System dependencies (iw, wireless-tools)

### 2. Create Virtual Monitor Interface

```bash
# Find your wireless interface
iw dev

# Create virtual monitor interface (WiFi stays connected!)
sudo ./monitor_mode.sh wlp0s20f3 setup
```

### 3. Run Sniffy Tester

```bash
# Simple broadcast (note: use virtual interface 'wlp0s20f3mon')
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon -c 6

# With ESP32 monitoring (auto-detect serial port)
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon --monitor

# Flood mode (20 unique MACs)
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon --flood -n 20
```

### 4. Remove Virtual Interface

```bash
sudo ./monitor_mode.sh wlp0s20f3 restore
```

## Usage Examples

### Test Basic Beacon Detection

```bash
# Broadcast on channel 6 (use virtual interface)
sudo python3 sniffy_tester.py -s "ESP32_TEST" -i wlp0s20f3mon -c 6

# ESP32 should detect beacons when it scans channel 6
```

### Test Channel Hopping

```bash
# Broadcast on channel 11
sudo python3 sniffy_tester.py -s "CH11_TEST" -i wlp0s20f3mon -c 11

# Enable hopping on ESP32 via serial:
#   hopping ON

# ESP32 will detect beacons when it hops to channel 11
```

### Test with Live Monitoring

```bash
# Broadcast and watch ESP32 serial in real-time
sudo python3 sniffy_tester.py -s "INTEGRATED_TEST" -i wlp0s20f3mon --monitor

# You'll see:
# - Beacons being sent
# - ESP32 output (highlighted when your SSID is detected)
# - Detection statistics
```

### Flood Mode (Trigger Multiple Detections)

```bash
# Send 20 beacons with different MACs
sudo python3 sniffy_tester.py -s "FLOOD_TEST" -i wlp0s20f3mon --flood -n 20 -t 1.0

# ESP32 will print [NEW DEVICE] for each unique MAC
```

### Custom Configuration

```bash
# Specific MAC address
sudo python3 sniffy_tester.py -s "CustomAP" -i wlp0s20f3mon -m "DE:AD:BE:EF:CA:FE"

# Open network (no encryption)
sudo python3 sniffy_tester.py -s "OpenWiFi" -i wlp0s20f3mon --open

# Faster beacons
sudo python3 sniffy_tester.py -s "FastAP" -i wlp0s20f3mon -t 0.05

# Specific serial port
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon --monitor --serial /dev/ttyACM0
```

## Command Reference

```
sniffy_tester.py [-h] -s SSID [options]

Required:
  -s, --ssid SSID           SSID to broadcast
  -i, --interface IFACE     Monitor interface (e.g., wlp0s20f3)

Optional:
  -c, --channel CH          Channel 1-14 (default: 6)
  -m, --mac MAC             MAC address (random if not specified)
  -t, --interval SEC        Beacon interval in seconds (default: 0.1)
  --open                    Broadcast as open network

Test Modes:
  --flood                   Flood mode: unique MACs for each beacon
  -n, --count N             Flood mode: number of beacons (default: 20)
  --monitor                 Monitor ESP32 serial output

Serial Options:
  --serial PORT             ESP32 serial port (auto-detect if omitted)
  --baudrate BAUD           Serial baudrate (default: 115200)
```

## Typical Testing Workflow

### End-to-End ESP32 Test

```bash
# Terminal 1: Flash and monitor ESP32
pio run -t upload && pio device monitor

# Terminal 2: Create virtual monitor interface
sudo ./monitor_mode.sh wlp0s20f3 setup

# Terminal 3: Run integrated test (note: use 'wlp0s20f3mon' virtual interface)
sudo python3 sniffy_tester.py \
  -s "SNIFFY_TEST" \
  -i wlp0s20f3mon \
  -c 6 \
  --monitor

# Expected ESP32 output:
#   [NEW DEVICE] SNIFFY_TEST | RSSI: -XX | Ch: 6
```

### Test Each ESP32 Feature

**1. Passive Scanning**
```bash
sudo python3 sniffy_tester.py -s "PASSIVE_TEST" -i wlp0s20f3mon -c 6
# ESP32 should detect and log beacon
```

**2. Channel Hopping**
```bash
# Broadcast on channel 11
sudo python3 sniffy_tester.py -s "CH11_TEST" -i wlp0s20f3mon -c 11

# In ESP32 serial, enable hopping:
hopping ON

# ESP32 should detect when it hops to channel 11
```

**3. RSSI Measurement**
```bash
# Broadcast, then move laptop closer/farther from ESP32
sudo python3 sniffy_tester.py -s "RSSI_TEST" -i wlp0s20f3mon --monitor

# Watch RSSI values change in ESP32 output
```

**4. Device Tracking**
```bash
# Flood mode: 20 unique devices
sudo python3 sniffy_tester.py -s "TRACKING_TEST" -i wlp0s20f3mon --flood -n 20

# ESP32 should track 20 unique devices
```

## Project Structure

```
beacon_broadcaster/
├── sniffy_tester.py        # Main testing tool
├── config.py               # Configuration settings
├── monitor_mode.sh         # Monitor mode management
├── install.sh              # One-time installation
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── archive/               # Old/unused scripts
```

## Configuration

Edit `config.py` to change defaults:

```python
DEFAULT_CHANNEL = 6           # Default broadcast channel
DEFAULT_BEACON_INTERVAL = 0.1 # Seconds between beacons
FLOOD_COUNT = 20              # Default flood beacon count
SHOW_STATS_INTERVAL = 5       # Stats update interval
```

## Troubleshooting

### "Must run as root"
**Solution:** Use `sudo`
```bash
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon
```

### "No module named 'scapy'"
**Solution:** Install dependencies
```bash
sudo python3 -m pip install scapy pyserial
```

### "Operation not permitted" / "Device or resource busy"
**Solution:** Ensure virtual monitor interface is created
```bash
sudo ./monitor_mode.sh wlp0s20f3 setup
```

### Network adapter issues / WiFi not working properly
**Solution:** Run cleanup script to restore proper network state
```bash
sudo ./cleanup.sh
```
This will:
- Remove any virtual monitor interfaces
- Restore physical interfaces to managed mode
- Restart NetworkManager if needed
- Fix any adapter configuration issues

### ESP32 not detecting beacons

**Possible causes:**

1. **Channel mismatch**
   - ESP32 on channel 1, broadcast on channel 6
   - Solution: Lock ESP32 to channel 6 via serial: `channel 6`

2. **ESP32 channel hopping disabled**
   - Solution: Enable hopping: `hopping ON`
   - Or broadcast on ESP32's current channel

3. **Frequency band mismatch**
   - ESP32 only supports 2.4GHz (channels 1-14)
   - Don't use 5GHz channels

4. **Monitor mode not active**
   - Solution: `sudo ./monitor_mode.sh wlp0s20f3 setup`

### No ESP32 serial output

1. **Check connection**
   ```bash
   ls /dev/ttyUSB* /dev/ttyACM*
   ```

2. **Specify port manually**
   ```bash
   sudo python3 sniffy_tester.py -s "Test" -i wlp0s20f3 --monitor --serial /dev/ttyACM0
   ```

3. **Check baudrate** (default 115200)
   ```bash
   sudo python3 sniffy_tester.py -s "Test" -i wlp0s20f3 --monitor --baudrate 115200
   ```

## Integration with Sniffy ESP32 Project

This tool is designed to work with the Sniffy ESP32 war driving project:

```
esp32/
├── src/
│   ├── PacketSniffer.cpp      # Detects beacons from this tool
│   ├── CommandInterface.cpp   # Control via serial
│   └── RFScanner.cpp          # Channel hopping logic
├── misc/
│   └── beacon_broadcaster/    # This tool
└── Docz/
    └── *.md                   # Project documentation
```

## Technical Details

### Beacon Frame Structure

```
RadioTap Header
└─ 802.11 Management Frame (Type 0, Subtype 8)
    ├─ Addresses: Broadcast, BSSID, BSSID
    └─ Frame Body
        ├─ Timestamp
        ├─ Beacon Interval
        ├─ Capability (ESS ± Privacy)
        └─ Information Elements
            ├─ SSID
            ├─ Supported Rates
            ├─ DS Parameter Set (Channel)
            ├─ Traffic Indication Map
            └─ Extended Rates
```

### MAC Address Generation

- First byte: Locally administered (bit 1 = 1)
- Ensures no hardware conflicts
- Format: `02:XX:XX:XX:XX:XX` to `FE:XX:XX:XX:XX:XX`

### Virtual Monitor Interface Benefits

| Feature | Physical Adapter (Managed) | Virtual Monitor Interface |
|---------|---------------------------|---------------------------|
| WiFi Connectivity | ✓ Stays Connected | N/A (virtual interface) |
| Packet Injection | ✗ No | ✓ Yes |
| Promiscuous RX | ✗ Limited | ✓ Full |
| MAC Address | Hardware MAC | Unique virtual MAC |
| Use Case | Normal WiFi | Testing/Analysis |

**How it works:**
- Creates a virtual interface (e.g., `wlp0s20f3mon`) alongside your physical adapter
- Physical adapter stays in managed mode with active WiFi
- Virtual interface operates in monitor mode for packet injection
- Both interfaces share the same physical wireless card

## Security & Legal Notice

⚠️ **IMPORTANT WARNINGS:**

- **Authorization Required** - Only test on your own equipment
- **Educational Purpose** - For security research and ESP32 development
- **Legal Compliance** - Broadcasting may be regulated in your jurisdiction
- **No Malicious Use** - Do not interfere with legitimate networks

**Authorized Uses:**
- Testing your own ESP32 device
- Security research in controlled environments
- Educational demonstrations
- Development and debugging

**NOT Authorized:**
- Disrupting public WiFi
- Creating rogue access points
- Interfering with others' networks
- Any malicious activity

## Support

**Issues:** Part of ESP32 Sniffy project
**License:** Educational/Testing Use Only
**Author:** ESP32 War Driving Project

---

**Remember:** Always test responsibly and ethically! 🛡️
