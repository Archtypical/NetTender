# Sniffy Boi v1.1.0

**Standalone WiFi Security Research Platform**

A portable ESP32-based wardriving and WPA2 attack platform with interactive command interface, OLED feedback, and optimized performance. Built for authorized security testing, CTF competitions, and educational research.

## Overview

Sniffy Boi is a **single-engine WiFi packet capture platform** designed for wardriving, handshake collection, PMKID extraction, and wireless security testing. It operates in monitor mode (promiscuous WiFi capture) without requiring network connectivity, making it ideal for field research and standalone operation.

### Key Features

- **🎯 Single-Engine Architecture**: Optimized RF Scanner for maximum packet capture performance
- **📡 Monitor Mode Operation**: No WiFi connection needed - pure promiscuous packet capture
- **⌨️ Interactive Command Interface**: Wireless C2 (magic packets) + serial CLI for remote control
- **📟 OLED Status Display**: Real-time feedback with split-screen health monitoring
- **🔒 WPA/WPA2 Attacks**: Handshake capture, PMKID extraction, deauth attacks, beacon flooding
- **💾 Hashcat Export**: Mode 22000 format for offline password cracking
- **⚡ v1.1 Optimizations**: 33% faster display rendering, unified utilities, cleaner code
- **🔐 Session Locking**: MAC-based authentication for wireless command security

## What's New in v1.1

**Performance Improvements:**
- ✅ **33% faster display** - Font caching eliminates redundant setFont() calls
- ✅ **Zero heap allocations** - MAC formatting uses stack buffers
- ✅ **60% fewer font switches** - Reduced from 6-8 to 2-3 per frame

**Code Quality:**
- ✅ **Unified utilities** - Single Utils.h for all MAC address operations
- ✅ **Named constants** - Magic numbers replaced with self-documenting names
- ✅ **Version management** - Centralized versioning with build info display

**Developer Experience:**
- ✅ **Multi-environment builds** - Switch between v1.1, v1.1-debug, v1.0 easily
- ✅ **Git tagged releases** - Semantic versioning with detailed changelogs

See [VERSION_UPGRADE_SUMMARY.md](VERSION_UPGRADE_SUMMARY.md) for full details.

## Hardware Requirements

### Minimum Configuration
- **ESP32 Dev Board** (ESP32-S3 recommended)
- **4MB Flash** minimum (8MB recommended for future features)
- **128x64 OLED Display** (SSD1306, I2C interface)
- **USB power** supply or battery

### Tested Hardware
- ✅ **Arduino Nano ESP32** (primary development target - ESP32-S3)
- ✅ **ESP32 DevKit V1** (ESP32-WROOM-32)

### Display Connection
- **OLED Display**: SSD1306 128x64
- **Interface**: I2C
- **SDA**: A4 / GPIO 21 (depending on board)
- **SCL**: A5 / GPIO 22 (depending on board)
- **I2C Address**: 0x3C (typical)
- **Note**: Configure pins in [include/config.h](include/config.h)

## Quick Start

### 1. Install PlatformIO
```bash
pip install platformio
```

### 2. Build and Upload v1.1
```bash
# Clone repository
git clone <repository-url>
cd esp32

# Build, upload, and monitor (all in one)
pio run -e v1_1 --target upload --target monitor
```

### 3. Verify Version at Boot
You should see:
```
╔════════════════════════════════════════════════════════════╗
║                   SNIFFY BOI v1.1.0                        ║
║              Wardriving & WPA2 Attack Platform           ║
╚════════════════════════════════════════════════════════════╝

  Version:     v1.1.0
  Build:       Nov 11 2025 15:30:45
  Platform:    Arduino Nano ESP32

  Optimizations (v1.1):
    ✓ Font caching (33% faster display)
    ✓ Unified MAC utilities
    ✓ Named constants (improved readability)
```

See [QUICK_START_v1.1.md](QUICK_START_v1.1.md) for detailed upload instructions.

## Capabilities

### Attack Vectors

#### 1. **Handshake Capture** (WPA/WPA2)
Captures complete 4-way EAPOL handshakes for offline cracking:
- **Passive capture**: Monitors network for natural client connections
- **Active capture**: Triggers deauth to force handshake
- **EAPOL M1-M4 tracking**: Full handshake validation
- **Hashcat export**: Mode 22000 for hashcat/john

📖 See: [Docz/HANDSHAKE_CAPTURE_GUIDE.md](Docz/HANDSHAKE_CAPTURE_GUIDE.md)

#### 2. **PMKID Extraction** (Clientless)
Captures PMKIDs from AP beacons without client presence:
- **Passive PMKID**: Extracts from normal beacons
- **Active PMKID**: Sends association requests to trigger responses
- **Clientless attack**: No connected clients required
- **Faster than handshakes**: Single M1 frame needed

📖 See: [Docz/PMKID_ATTACK_GUIDE.md](Docz/PMKID_ATTACK_GUIDE.md)

#### 3. **Deauthentication Attacks**
Disconnects clients from target networks:
- **Targeted deauth**: Specific client MAC addresses
- **Broadcast deauth**: All clients on AP
- **Handshake trigger**: Force clients to reconnect for capture
- **Configurable duration**: 10-second attack window

📖 See: [Docz/DEAUTH_ATTACK_GUIDE.md](Docz/DEAUTH_ATTACK_GUIDE.md)

#### 4. **Beacon Flooding**
Creates fake access points for testing:
- **Mass SSID generation**: Floods WiFi list with fake APs
- **Random BSSIDs**: Each beacon has unique MAC
- **Configurable count**: 50-100 beacons per second
- **Denial of service**: Overwhelms WiFi scanners

📖 See: [Docz/BEACON_FLOOD_ATTACK_GUIDE.md](Docz/BEACON_FLOOD_ATTACK_GUIDE.md)

### Command Interface

Sniffy Boi features a **dual-interface command system** for remote control:

#### Wireless C2 (Magic Packets)
Control the device wirelessly by sending specially-crafted WiFi packets:
- **MAC-based authentication**: Session locking prevents unauthorized access
- **No network connection**: Works in monitor mode
- **Commands**: SCAN, DEAUTH, PMKID, HANDSHAKE, BEACONFLOOD, STATUS
- **Session management**: 2-minute timeout, automatic cooldown

#### Serial CLI
Interactive terminal via USB:
- **115200 baud** standard serial
- **Same commands** as wireless interface
- **Real-time feedback**: Attack progress and results
- **Debug logging**: Verbose output for troubleshooting

📖 See: [Docz/COMMAND_INTERFACE_GUIDE.md](Docz/COMMAND_INTERFACE_GUIDE.md)

### State Machine

Sniffy Boi uses a **state machine architecture** with 18 states for robust command handling:

```
IDLE ──> SCANNING ──> SCAN_COMPLETE ──> AWAITING_TARGET
                                              │
                 ┌────────────────────────────┴──────────────┐
                 │                                            │
                 v                                            v
           DEAUTH_ATTACK                              PMKID_ATTACK
                 │                                            │
                 v                                            v
           DEAUTH_COMPLETE                          PMKID_COMPLETE
                 │                                            │
                 └────────────────────> COOLDOWN <───────────┘
                                            │
                                            v
                                         IDLE
```

**Key Features:**
- **Session locking**: First wireless command locks to sender MAC
- **Timeout protection**: 2-minute idle timeout returns to IDLE
- **Cooldown enforcement**: 60-second cooldown after attacks
- **Error recovery**: Automatic state transitions on failures

📖 See: [Docz/INTERACTIVE_COMMAND_FLOW.md](Docz/INTERACTIVE_COMMAND_FLOW.md)

## Software Architecture

### Core Components

#### **EngineManager**
Manages the RF Scanner engine lifecycle:
- Power-On Self Test (POST) execution
- Auto-start logic at boot
- Health monitoring (5-second heartbeat)
- Engine initialization and cleanup

#### **RFScanner** (Main Engine)
WiFi packet capture and attack engine:
- **PacketSniffer**: Promiscuous mode 802.11 frame parsing
- **PMKIDCapture**: Clientless PMKID extraction module
- **Handshake tracking**: EAPOL M1-M4 sequence detection
- **Attack execution**: Deauth and beacon flooding
- **Device tracking**: RSSI, channel, encryption statistics

#### **CommandInterface**
Dual-mode command processor:
- Wireless C2 via magic packet detection
- Serial CLI via USB terminal
- State machine with 18 states
- MAC-based session authentication
- Timeout and cooldown enforcement

#### **CommandLedger**
Persistent state storage using LittleFS:
- Saves command state to filesystem
- Session MAC tracking
- Attack target persistence
- Survives reboots and crashes

#### **SystemLogger**
6-level logging system:
- **INFORMATIONAL**: General operation logs
- **WARNING**: Non-critical issues
- **ERROR**: Recoverable failures
- **CRITICAL**: Severe errors (shown on OLED)
- **FLAGGED**: Important events (shown on OLED)
- **SUCCESS**: Completed operations (shown on OLED)

#### **DisplayManager** (v1.1 Optimized)
Split-screen OLED interface with font caching:
- **Left panel**: Engine health status (OK/ERR indicators)
- **Right panel**: Live log stream (last 3-4 events)
- **Font caching**: 33% faster rendering
- **Progress bars**: Attack duration visualization
- **Boot sequence**: POST status and progress

### Packet Capture System

#### WiFi Monitor Mode
Operates in ESP32's promiscuous mode for raw 802.11 frame capture:
- **Channel hopping**: Scans all 13 WiFi channels (configurable)
- **Frame types**: Beacons, probe requests/responses, data, management
- **ISR-safe callbacks**: Interrupt-safe packet handling
- **Device tracking**: MAC address resolution and statistics

#### ISR-Safe Design Pattern
Critical for WiFi packet callbacks that run in interrupt context:

```cpp
// PacketSniffer uses static members for ISR context
class PacketSniffer {
    static PacketSniffer* instance;
    static void IRAM_ATTR promiscuousCallback(void* buf, wifi_promiscuous_pkt_type_t type);
};
```

**ISR Restrictions:**
- ❌ No dynamic memory allocation (`new`, `malloc`, `String`)
- ❌ No Serial/display I/O
- ❌ No FreeRTOS synchronization
- ✅ Use static buffers and flags
- ✅ Defer processing to main loop

## Memory Usage (v1.1)

### Flash Memory
```
Used:      852,017 bytes (43.3% of 1,966,080 bytes)
Available: 1,114,063 bytes (56.7% free)

Binary breakdown:
  firmware.bin:   852 KB
  bootloader.bin: 17 KB
  partitions.bin: 3 KB
```

### RAM Usage
```
Compile-time: 45,048 bytes (13.7% of 327,680 bytes)
Runtime:      Variable (packet buffers, logs, handshakes)
Available:    282,632 bytes (86.3% free)
```

**v1.1 vs v1.0:**
- Flash: +0.7 KB (version strings and optimization code)
- RAM: No change
- Performance: 33% faster display, zero heap allocations for MAC ops

## Build System

Sniffy Boi v1.1 supports **multi-environment builds** for easy version switching:

### Available Environments

| Environment | Purpose | When to Use |
|-------------|---------|-------------|
| **v1_1** ⭐ | Current optimized build | Production, daily use |
| **v1_1_debug** | Debug build with verbose logging | Development, troubleshooting |
| **v1_0** | Legacy pre-optimization | Comparison, rollback |
| **esp32dev** | Backward compatibility alias | If you used this before |

### Build Commands

```bash
# Build v1.1 (recommended)
pio run -e v1_1

# Build with debug symbols
pio run -e v1_1_debug

# Build v1.0 (requires git checkout first)
git checkout v1.0
pio run -e v1_0
git checkout main
```

### Upload Commands

```bash
# Upload v1.1 (one-liner with monitor)
pio run -e v1_1 --target upload --target monitor

# Upload to specific port
pio run -e v1_1 --target upload --upload-port /dev/ttyUSB0

# Upload debug build
pio run -e v1_1_debug --target upload
```

📖 See: [BUILD_GUIDE.md](BUILD_GUIDE.md) for comprehensive build instructions.

## Configuration

### Compile-Time Settings

Edit `include/config.h` for hardware and behavior settings:

```cpp
// WiFi Configuration (not used in monitor mode, but required for ESP32 init)
#define WIFI_SSID           "YourWiFi"
#define WIFI_PASSWORD       "password"

// Operation Mode
#define MODE_DUAL_ENGINE        true   // Legacy - only RF Scanner runs now
#define AUTO_START_ON_BOOT      true   // Auto-start RF Scanner at boot
#define BOOT_HEALTH_CHECK       true   // Run Power-On Self Test

// Channel Hopping
#define ENABLE_CHANNEL_HOPPING  true   // Scan all 13 channels
#define CHANNEL_HOP_INTERVAL    1000   // 1 second per channel
#define START_CHANNEL           1
#define MAX_CHANNEL             13

// Display Configuration
#define OLED_I2C_ADDRESS        0x3C
#define OLED_SDA_PIN            A4     // Arduino Nano ESP32
#define OLED_SCL_PIN            A5
```

### No Network Configuration Needed

**Note:** Sniffy Boi v1.1 operates in **standalone monitor mode** and does NOT require WiFi network connectivity. The WiFi credentials in config.h are legacy settings kept for ESP32 initialization compatibility but are not used during operation.

**Removed:** `NetworkConfig.h` (all networking protocols removed in v1.0)

## Boot Sequence

1. **Hardware Initialization** (main.cpp)
   - Serial console @ 115200 baud
   - DisplayManager (OLED on I2C)
   - SystemLogger (100-entry ring buffer)
   - EngineManager

2. **Power-On Self Test (POST)**
   - Display functional test
   - WiFi hardware validation
   - Memory check (minimum 50 KB free heap)
   - Results displayed on OLED with progress bar

3. **Engine Auto-Start**
   - RF Scanner initializes
   - WiFi promiscuous mode enabled
   - PacketSniffer and PMKIDCapture modules ready
   - Engine registers with logger

4. **Operational State**
   - Split-screen OLED shows engine health and logs
   - Command interface active (serial + wireless)
   - Channel hopping begins (if enabled)
   - Device enters main loop

## Display Layout

### Boot Sequence View
```
+---------------------------+
|    Sniffy Boi v1.1.0      |
|                           |
|  [Display]: OK            |
|  [WiFi]:    OK            |
|  [Memory]:  OK            |
|                           |
|  [===========>      ] 75% |
+---------------------------+
```

### Operational View (Split-Screen)
```
+------------+-------------+
| RF Scanner | 12:34:56    |
|    OK      | SUCCESS     |
|            | RFScanner   |
| Errors: 0  | Handshake   |
| Warns:  0  | Captured    |
|            |             |
|            | 12:34:58    |
|            | CRITICAL    |
+------------+-------------+
 Left: Health | Right: Logs
```

### Command Execution Feedback
```
+---------------------------+
|    DEAUTH ATTACK          |
|                           |
|  Target: AA:BB:CC:DD:EE:FF|
|  Duration: 10s            |
|                           |
|  [=======>         ] 60%  |
+---------------------------+
```

## Documentation

### Quick Start Guides
- **[QUICK_START_v1.1.md](QUICK_START_v1.1.md)** - 30-second upload guide
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Multi-version build system
- **[VERSION_UPGRADE_SUMMARY.md](VERSION_UPGRADE_SUMMARY.md)** - v1.0 to v1.1 upgrade

### Attack Guides
- **[Docz/HANDSHAKE_CAPTURE_GUIDE.md](Docz/HANDSHAKE_CAPTURE_GUIDE.md)** - WPA/WPA2 handshake capture
- **[Docz/PMKID_ATTACK_GUIDE.md](Docz/PMKID_ATTACK_GUIDE.md)** - Clientless PMKID extraction
- **[Docz/DEAUTH_ATTACK_GUIDE.md](Docz/DEAUTH_ATTACK_GUIDE.md)** - Deauthentication attacks
- **[Docz/BEACON_FLOOD_ATTACK_GUIDE.md](Docz/BEACON_FLOOD_ATTACK_GUIDE.md)** - Beacon flooding

### Architecture Documentation
- **[Docz/COMMAND_INTERFACE_GUIDE.md](Docz/COMMAND_INTERFACE_GUIDE.md)** - Wireless C2 and serial CLI
- **[Docz/INTERACTIVE_COMMAND_FLOW.md](Docz/INTERACTIVE_COMMAND_FLOW.md)** - State machine design
- **[Docz/PROJECT_STRUCTURE.md](Docz/PROJECT_STRUCTURE.md)** - File organization
- **[Docz/LANGUAGE_ARCHITECTURE_REPORT.md](Docz/LANGUAGE_ARCHITECTURE_REPORT.md)** - Code analysis
- **[Docz/CLAUDE.md](Docz/CLAUDE.md)** - Development context for AI assistants

### Optimization Documentation
- **[Docz/OPTIMIZATION_MASTER.md](Docz/OPTIMIZATION_MASTER.md)** - Complete optimization analysis
- **[Docz/OPTIMIZATIONS_APPLIED.md](Docz/OPTIMIZATIONS_APPLIED.md)** - v1.1 implementation summary

## Use Cases

### Authorized Security Testing
- **Penetration testing**: Authorized network security assessments
- **WiFi auditing**: Evaluating WPA/WPA2 security strength
- **Client testing**: Validating device security configurations
- **Red team exercises**: Simulating wireless attacks

### Wardriving and Research
- **WiFi mapping**: Discovering access points in an area
- **Encryption surveys**: Documenting security protocol usage
- **SSID collection**: Building WiFi network databases
- **Channel analysis**: Understanding frequency utilization

### Educational Contexts
- **Security courses**: Demonstrating wireless attack vectors
- **CTF competitions**: Capture The Flag wireless challenges
- **Lab environments**: Hands-on security training
- **Research projects**: Academic wireless security studies

## Troubleshooting

### Build Issues

**"Utils.h not found"**
```bash
# Ensure you have all v1.1 files
git pull
git checkout main
ls include/Utils.h  # Should exist
```

**Build fails after git pull**
```bash
# Clean and rebuild
pio run --target clean
rm -rf .pio
pio run -e v1_1
```

### Upload Issues

**"Could not open port /dev/ttyACM0"**
```bash
# Add user to dialout group (Linux)
sudo usermod -a -G dialout $USER
# Log out and back in, then try again
```

**Device not found**
```bash
# List available ports
pio device list

# Use correct port
pio run -e v1_1 --target upload --upload-port /dev/ttyUSB0
```

### Runtime Issues

**OLED display blank**
- Check I2C connections (SDA: A4, SCL: A5)
- Verify OLED address (run I2C scanner: 0x3C typical)
- Check power supply (3.3V or 5V depending on module)

**POST failures**
- Display test fails: Check I2C wiring
- WiFi test fails: Verify ESP32 module
- Memory test fails: Reduce SystemLogger maxEntries

**No packets captured**
- Verify WiFi channel matches target AP
- Disable channel hopping for targeted capture
- Check antenna connection
- Ensure monitor mode enabled (check serial output)

**Version shows v1.0 instead of v1.1**
```bash
# Explicitly upload v1_1 environment
pio run -e v1_1 --target upload

# Verify with serial monitor
pio device monitor --baud 115200
# Look for "SNIFFY BOI v1.1.0" in boot banner
```

## Security Considerations

### ⚠️ Authorized Use Only

This platform is designed for:
- ✅ **Authorized security testing** with written permission
- ✅ **Networks you own** or have explicit authorization to test
- ✅ **CTF competitions** and hacking challenges
- ✅ **Educational contexts** with proper supervision
- ✅ **Defensive security research** in controlled environments

### ❌ Prohibited Activities

Do **NOT** use Sniffy Boi for:
- ❌ Unauthorized network access or testing
- ❌ Disrupting network services (DoS attacks)
- ❌ Mass targeting of networks or devices
- ❌ Intercepting others' communications without authorization
- ❌ Any activity violating local/national laws

### Legal Notice

**Unauthorized use of wireless security tools may violate:**
- Computer Fraud and Abuse Act (CFAA) - USA
- Unauthorized access statutes
- Wireless communication regulations
- Local and international cybercrime laws

**Users are solely responsible** for ensuring their use complies with all applicable laws and regulations. The developers assume no liability for misuse.

## Development Status

### Implemented Features (v1.1.0) ✅
- ✅ Single-engine RF Scanner architecture
- ✅ WiFi monitor mode (promiscuous packet capture)
- ✅ Complete WPA/WPA2 handshake capture (EAPOL M1-M4)
- ✅ PMKID extraction (passive + clientless attack)
- ✅ Deauthentication attacks (targeted + broadcast)
- ✅ Beacon flooding
- ✅ Interactive command interface (wireless C2 + serial CLI)
- ✅ State machine with MAC-based session locking
- ✅ OLED display with split-screen layout
- ✅ Hashcat mode 22000 export
- ✅ Channel hopping (13 channels)
- ✅ Device tracking and statistics
- ✅ Filesystem state persistence (LittleFS)
- ✅ Font caching optimization (33% faster)
- ✅ Unified MAC utilities (zero heap allocations)
- ✅ Multi-environment build system

### Removed Features (v1.0 → v1.1) ❌
- ❌ NetworkAnalyzer engine (focus on WiFi attacks)
- ❌ WebInterface and HTTP server (attack surface reduction)
- ❌ TelnetServer (security hardening)
- ❌ Cloud storage protocols (WebDAV, S3, HTTP upload)
- ❌ ArduinoJson dependency (lighter footprint)

**Result:** Freed 162 KB flash, simplified codebase, better performance

### Planned Features 🚀
- [ ] **SD card logging** - PCAP export and long-term storage
- [ ] **GPS integration** - Wardriving with lat/lon coordinates
- [ ] **OLED menu system** - Attack mode selection without serial
- [ ] **Auto-attack mode** - Deauth all clients on channel
- [ ] **WPA3 detection** - Identify and flag WPA3 networks
- [ ] **Bluetooth scanning** - BLE device discovery
- [ ] **Battery monitoring** - Power level tracking
- [ ] **Sleep mode** - Power conservation for portable use

## Contributing

Contributions welcome! Areas of interest:

- **SD card logging** - PCAP format export
- **GPS module integration** - Wardriving coordinates
- **Performance optimizations** - Further speed improvements
- **Documentation improvements** - Clarity and examples
- **Bug fixes** - Testing and issue resolution
- **Hardware testing** - Validation on different ESP32 boards

### Development Guidelines

- Follow existing code structure and naming conventions
- Use `Utils.h` for MAC address operations (no duplicates!)
- Use named constants instead of magic numbers
- Preserve ISR-safe patterns in packet callbacks
- Test on real hardware before submitting
- Keep memory usage minimal (target <50% flash, <20% RAM)
- Document all public APIs with comments

### Testing Checklist

Before submitting changes:
- [ ] Builds without errors on v1_1 environment
- [ ] Uploads and boots successfully
- [ ] Version banner shows correct info
- [ ] All commands work via serial
- [ ] Wireless C2 commands work
- [ ] OLED display updates correctly
- [ ] No memory leaks (check free heap)
- [ ] Code follows project conventions

## References

### ESP32 Documentation
- ESP-IDF Programming Guide: https://docs.espressif.com/projects/esp-idf/
- Arduino-ESP32 Reference: https://docs.espressif.com/projects/arduino-esp32/
- WiFi Promiscuous Mode: ESP32 Technical Reference Manual

### Libraries
- U8g2 OLED Library: https://github.com/olikraus/u8g2
- PlatformIO: https://platformio.org/

### Wireless Security
- 802.11 Frame Types: IEEE 802.11 Standard
- WPA2 4-Way Handshake: Wi-Fi Alliance Documentation
- PMKID Attack: https://hashcat.net/forum/thread-7717.html
- Hashcat Mode 22000: https://hashcat.net/wiki/doku.php?id=cracking_wpawpa2

## License

This project is provided **as-is** for educational and authorized security research purposes.

**No warranty** is provided. Users assume all responsibility for compliance with applicable laws.

---

## Quick Reference Card

### Build Commands
```bash
pio run -e v1_1                          # Build v1.1
pio run -e v1_1 --target upload          # Upload v1.1
pio run -e v1_1 --target upload --target monitor  # Upload + monitor
pio device monitor --baud 115200         # Serial monitor only
```

### Attack Commands (Serial/Wireless)
```
scan                    - Scan for WiFi networks
deauth <MAC>            - Deauth specific client
deauth FF:FF:FF:FF:FF:FF - Deauth all clients
pmkid <BSSID>           - Capture PMKID from AP
handshake <BSSID>       - Trigger handshake capture
beaconflood             - Start beacon flooding
status                  - Show current state
help                    - List all commands
```

### Memory Stats
- Flash: 852 KB (43.3%)
- RAM: 45 KB (13.7%)
- **56.7% flash available** for future features

### Version Info
- **Current**: v1.1.0 (Nov 11, 2025)
- **Previous**: v1.0.0
- **Git Tag**: v1.1.0

---

**Disclaimer**: This tool is for **educational and authorized security testing only**. Unauthorized network access, disruption, or interception is **illegal and unethical**. Always obtain proper authorization before conducting security research.

**Enjoy Sniffy Boi v1.1! 🎯**
