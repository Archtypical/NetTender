# Sniffy Tester Module

**Version:** 1.1
**Created:** 2025-11-10
**Updated:** 2025-11-11
**Purpose:** WiFi beacon broadcasting for ESP32 Sniffy testing

**v1.1 Changes:**
- Implemented virtual monitor interface approach
- WiFi stays connected during testing
- Safer network configuration management
- Updated all scripts and documentation

## Module Structure

```
beacon_broadcaster/
├── sniffy_tester.py       # Main unified testing tool (540 lines)
├── config.py              # Centralized configuration (40 lines)
├── monitor_mode.sh        # Monitor mode setup/teardown (120 lines)
├── install.sh             # One-time installation script (80 lines)
├── cleanup.sh             # System cleanup utility (120 lines)
├── requirements.txt       # Python dependencies (scapy, pyserial)
├── README.md             # Complete documentation (370 lines)
├── QUICKSTART.md         # Quick reference guide
└── archive/              # Old/experimental scripts
```

## Core Features

### 1. Unified Testing Tool (`sniffy_tester.py`)

**Three Operating Modes:**
- **Simple Mode:** Continuous broadcast with single MAC
- **Flood Mode:** Multiple beacons with unique MACs
- **Integrated Mode:** Broadcast + ESP32 serial monitoring

**Key Capabilities:**
- 2.4GHz WiFi (channels 1-14)
- Custom SSID and MAC address
- Encrypted or open network simulation
- Real-time ESP32 serial output
- Auto-detect ESP32 serial port
- Live statistics display

### 2. Configuration System (`config.py`)

Centralized settings for:
- Default channel (6)
- Beacon interval (0.1s)
- Flood count (20 beacons)
- ESP32 detection keywords
- Display preferences

### 3. Monitor Mode Manager (`monitor_mode.sh`)

**Setup Mode:**
- Creates a **virtual monitor interface** (e.g., `wlp0s20f3mon`)
- Physical interface remains in managed mode
- WiFi connectivity is preserved
- Virtual interface configured for packet injection
- NetworkManager instructed to ignore monitor interface

**Restore Mode:**
- Removes virtual monitor interface
- Physical interface remains unaffected
- No need to restart NetworkManager
- WiFi stays connected throughout

### 4. Installation (`install.sh`)

Automated setup:
- Detects Linux distribution (Fedora/Debian/Ubuntu)
- Installs system dependencies (iw, wireless-tools)
- Installs Python packages system-wide (for sudo)
- Verifies installation
- Auto-detects wireless interface

### 5. Cleanup Utility (`cleanup.sh`)

Comprehensive cleanup:
- Terminates beacon broadcaster processes
- Removes **virtual** monitor interfaces (ending with 'mon')
- Checks if physical interfaces are stuck in monitor mode
- Only restarts NetworkManager if physical interfaces were affected
- Cleans Python cache
- Safe and non-destructive to network configuration

## Usage Workflow

### First Time (One-Time Setup)
```bash
cd /home/user/Projects/esp32/misc/beacon_broadcaster
./install.sh
```

### Every Test Session

**Step 1: Create Virtual Monitor Interface**
```bash
sudo ./monitor_mode.sh wlp0s20f3 setup
# Creates wlp0s20f3mon virtual interface, WiFi stays connected!
```

**Step 2: Run Test (use virtual interface)**
```bash
# Simple broadcast (note: use 'wlp0s20f3mon')
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon -c 6

# OR: Flood mode
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon --flood -n 20

# OR: Integrated monitoring
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon --monitor
```

**Step 3: Remove Virtual Interface**
```bash
sudo ./monitor_mode.sh wlp0s20f3 restore
# Removes wlp0s20f3mon, physical interface unaffected
```

### Emergency Cleanup
```bash
sudo ./cleanup.sh
```

## Technical Implementation

### Beacon Frame Construction

```python
RadioTap Header (variable length)
└─ 802.11 Management Frame
    ├─ Type: 0 (Management)
    ├─ Subtype: 8 (Beacon)
    ├─ Addresses: Broadcast, BSSID, BSSID
    └─ Frame Body
        ├─ Timestamp (8 bytes)
        ├─ Beacon Interval (2 bytes)
        ├─ Capability Info (2 bytes)
        └─ Information Elements
            ├─ SSID (variable)
            ├─ Supported Rates
            ├─ DS Parameter Set (channel)
            ├─ TIM (Traffic Indication Map)
            └─ Extended Rates
```

### MAC Address Generation

- Locally administered (bit 1 = 1)
- Unicast (bit 0 = 0)
- Format: `02:XX:XX:XX:XX:XX` to `FE:XX:XX:XX:XX:XX`
- Ensures no hardware conflicts

### Serial Monitoring

- Background thread for non-blocking I/O
- Queue-based communication
- Keyword detection for statistics
- Colored output for SSID matches

## Integration with Sniffy ESP32

### ESP32 Side (C++)
```cpp
PacketSniffer::processBeacon()  // Receives beacons
CommandInterface::handleChannel() // Lock to channel
CommandLedger::setHopping()     // Enable/disable hopping
```

### Python Side
```python
sniffy_tester.py --monitor      // Watches ESP32 output
SerialMonitor class             // Parses [NEW DEVICE] etc.
```

## Dependencies

**System:**
- `iw` - Wireless interface management
- `wireless-tools` - Additional WiFi utilities
- `python3-dev` - Python development headers
- `libpcap-dev` - Packet capture library

**Python:**
- `scapy>=2.5.0` - Packet crafting and injection
- `pyserial>=3.5` - ESP32 serial communication

## Design Decisions

### Why Virtual Interfaces?

**Current Approach (v1.1+):**
- Creates virtual monitor interface (e.g., `wlp0s20f3mon`)
- Physical interface stays in managed mode with WiFi connected
- Virtual interface operates in monitor mode for packet injection
- Both interfaces share the same physical wireless card

**Benefits:**
- **No WiFi disconnection** - Stay connected while testing
- **Independent operation** - Physical and virtual interfaces don't interfere
- **Unique MAC addresses** - Virtual interface gets its own MAC
- **Safe and reversible** - Easy to remove without affecting physical adapter

**Compatibility:**
- Works with most modern wireless drivers (mac80211-based)
- Intel, Atheros, Realtek chipsets supported
- Requires driver support for virtual interfaces (`iw phy` shows capabilities)

### Why Single Script vs. Multiple?

**Old Approach (16 files):**
- beacon_broadcast.py, integrated_test.py, flood_test.py
- setup.sh, test_setup.sh, test_esp32.sh
- Confusing workflow

**New Approach (8 files):**
- sniffy_tester.py (unified, 3 modes)
- Clear separation of concerns
- One script to learn

### Why System-Wide pip Install?

- Scripts require `sudo` for packet injection
- Root user needs access to Python packages
- `sudo pip install` puts packages in system path
- User-level installs (`~/.local`) not visible to root

## Testing Scenarios

### 1. Basic Detection Test
```bash
sudo python3 sniffy_tester.py -s "ESP32_TEST" -i wlp0s20f3mon -c 6
# ESP32 should show: [NEW DEVICE] ESP32_TEST | RSSI: -XX | Ch: 6
```

### 2. Channel Hopping Test
```bash
# Broadcast on channel 11
sudo python3 sniffy_tester.py -s "CH11_TEST" -i wlp0s20f3mon -c 11

# ESP32 serial: hopping ON
# ESP32 detects when it hops to channel 11
```

### 3. Device Tracking Test
```bash
# Flood 20 unique devices
sudo python3 sniffy_tester.py -s "TRACKING" -i wlp0s20f3mon --flood -n 20
# ESP32 should track 20 unique MAC addresses
```

### 4. RSSI Measurement Test
```bash
# Monitor while moving laptop closer/farther
sudo python3 sniffy_tester.py -s "RSSI_TEST" -i wlp0s20f3mon --monitor
# Watch RSSI values change in real-time
```

## Security Notes

### Authorized Use Only
- Test on your own equipment
- Educational purposes
- Security research in controlled environments
- ESP32 development and debugging

### Not Authorized For
- Disrupting public WiFi networks
- Creating rogue access points for malicious purposes
- Interfering with others' communications
- Any illegal activity

### Legal Compliance
- Broadcasting RF signals is regulated
- WiFi jamming may be illegal in your jurisdiction
- Always obtain proper authorization
- Follow local laws and regulations

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| "Must run as root" | Use `sudo` |
| "No module 'scapy'" | `sudo python3 -m pip install scapy pyserial` |
| "Operation not permitted" | Enable monitor mode first |
| ESP32 not detecting | Check channel match (both on channel 6) |
| No serial output | Verify ESP32 connection, check port |
| WiFi won't restore | Run `sudo ./cleanup.sh` |

## Future Enhancements

Potential additions:
- GUI interface for non-technical users
- Automated test suite runner
- Multiple simultaneous SSIDs
- Probe request injection
- Deauth frame generation
- Channel auto-detection from ESP32

## Archive

Old experimental scripts preserved in `archive/` directory:
- Virtual NIC approach (didn't work on Intel cards)
- Multiple specialized scripts (replaced by unified tool)
- Original troubleshooting guides (merged into README)

See `archive/README_ARCHIVE.md` for details.

---

**Maintainer:** ESP32 Sniffy Project
**License:** Educational/Testing Use Only
**Last Updated:** 2025-11-10
