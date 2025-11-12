# Sniffy Boi v1.1 - Project Structure

**Single-Engine WiFi Security Research Platform**

---

## Pre-Build Structure

```
esp32/
├── include/                    # Header files
│   ├── CommandInterface.h      # Interactive command processor (serial + wireless C2)
│   ├── CommandLedger.h         # Persistent state storage (LittleFS)
│   ├── config.h                # Operational mode configuration
│   ├── DisplayManager.h        # OLED display interface (SSD1306) with font caching
│   ├── EngineManager.h         # Engine lifecycle manager
│   ├── PacketSniffer.h         # WiFi promiscuous mode packet capture
│   ├── PMKIDCapture.h          # Clientless PMKID extraction module
│   ├── RFScanner.h             # RF scanner engine (main)
│   ├── SystemLogger.h          # 6-level logging system
│   ├── Utils.h                 # Unified MAC address utilities (v1.1)
│   └── version.h               # Version management system (v1.1)
│
├── src/                        # Implementation files
│   ├── CommandInterface.cpp    # Command processing logic
│   ├── CommandLedger.cpp       # Filesystem state persistence
│   ├── DisplayManager.cpp      # OLED rendering with font caching
│   ├── EngineManager.cpp       # Engine management logic
│   ├── main.cpp                # Application entry point
│   ├── PacketSniffer.cpp       # Packet capture implementation
│   ├── PMKIDCapture.cpp        # PMKID attack implementation
│   ├── RFScanner.cpp           # RF scanner implementation
│   └── SystemLogger.cpp        # Logging system implementation
│
├── Docz/                       # Documentation
│   ├── README.md               # Documentation index
│   ├── QUICK_START.md          # Quick start guide
│   ├── CLAUDE.md               # AI assistant guidance
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── LANGUAGE_ARCHITECTURE_REPORT.md  # Codebase analysis
│   ├── COMMAND_INTERFACE_GUIDE.md       # Command reference
│   ├── INTERACTIVE_COMMAND_FLOW.md      # State machine design
│   ├── HANDSHAKE_CAPTURE_GUIDE.md       # Handshake capture tutorial
│   ├── PMKID_ATTACK_GUIDE.md            # PMKID attack guide
│   ├── DEAUTH_ATTACK_GUIDE.md           # Deauth attack guide
│   ├── BEACON_FLOOD_ATTACK_GUIDE.md     # Beacon flooding guide
│   ├── OPTIMIZATION_MASTER.md           # Optimization analysis
│   ├── OPTIMIZATIONS_APPLIED.md         # v1.1 optimization summary
│   └── DOCUMENTATION_AUDIT_REPORT.md    # Documentation accuracy audit
│
├── lib/                        # External libraries (empty, using PlatformIO registry)
├── .claude/                    # Claude Code configuration
│   └── settings.local.json    # Local Claude settings
├── .vscode/                    # VSCode configuration
│   └── extensions.json        # Recommended extensions
│
├── platformio.ini              # PlatformIO build configuration (multi-environment)
├── partitions.csv              # Flash memory partition table
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
├── BUILD_GUIDE.md              # Build system documentation
├── VERSION_UPGRADE_SUMMARY.md  # v1.0 to v1.1 upgrade guide
├── QUICK_START_v1.1.md         # Fast-track upload guide
└── test_i2c_scanner.cpp        # I2C device scanner utility
```

---

## Post-Build Structure

```
esp32/
├── [All pre-build files above]
│
├── .pio/                       # PlatformIO build system (generated)
│   ├── build/
│   │   ├── v1_1/               # v1.1 optimized build (default)
│   │   │   ├── firmware.elf        # ELF executable with debug symbols
│   │   │   ├── firmware.bin        # Main application binary (852 KB)
│   │   │   ├── bootloader.bin      # ESP32 bootloader (17 KB)
│   │   │   ├── partitions.bin      # Partition table (3 KB)
│   │   │   ├── src/                # Compiled object files (*.o)
│   │   │   ├── lib*/               # Compiled library archives
│   │   │   └── FrameworkArduino/   # Arduino framework objects
│   │   │
│   │   ├── v1_1_debug/         # v1.1 debug build
│   │   │   └── [same as v1_1 but with debug symbols]
│   │   │
│   │   └── v1_0/               # v1.0 legacy build (requires git checkout)
│   │       └── [legacy pre-optimization build]
│   │
│   ├── libdeps/                # Downloaded library dependencies
│   │   └── v1_1/
│   │       └── U8g2/           # OLED display library (only dependency)
│   │
│   └── penv/                   # Python virtual environment
│
└── .git/                       # Git repository
    └── [version control data]
```

---

## Key Files Description

### Configuration Files

#### **platformio.ini**
Multi-environment build system configuration:
- **Environments:**
  - `v1_1` - Current optimized build (default) ⭐
  - `v1_1_debug` - Debug build with verbose logging
  - `v1_0` - Legacy pre-optimization build
  - `esp32dev` - Backward compatibility alias
- **Board:** Arduino Nano ESP32 (ESP32-S3)
- **Platform:** espressif32
- **Framework:** Arduino
- **Libraries:** U8g2 @ ^2.35.9 (only dependency)
- **Build flags:**
  - PSRAM support (`-DBOARD_HAS_PSRAM`)
  - USB CDC enabled (`-DARDUINO_USB_CDC_ON_BOOT=1`)
  - Debug level 1 (minimal logging)
  - Bluetooth disabled (saves 145 KB flash)
- **Upload:** /dev/ttyACM0 at 115200 baud with custom reset flags

#### **partitions.csv**
Flash memory partition table:
- Bootloader partition
- Application partition (firmware)
- NVS (Non-Volatile Storage)
- LittleFS (filesystem for CommandLedger state persistence)

#### **include/config.h**
Operational configuration:
- WiFi credentials (legacy, not used in monitor mode)
- Boot behavior (`AUTO_START_ON_BOOT`, `BOOT_HEALTH_CHECK`)
- Display pin configuration (I2C: A4/A5 for Arduino Nano ESP32)
- Channel hopping settings (`ENABLE_CHANNEL_HOPPING`, `CHANNEL_HOP_INTERVAL`)
- Attack durations and timeouts

---

### Core System Files

#### **src/main.cpp**
Application entry point:
- System initialization (Serial, DisplayManager, SystemLogger, EngineManager)
- Version info display (via `printVersionInfo()` from version.h)
- Power-On Self Test (POST) execution
- Engine auto-start
- Main loop coordination

#### **include/version.h** (NEW in v1.1)
Centralized version management:
- Version constants (`SNIFFY_VERSION_MAJOR`, `SNIFFY_VERSION_MINOR`, `SNIFFY_VERSION_PATCH`)
- Version string generation (`SNIFFY_VERSION_STRING = "v1.1.0"`)
- `printVersionInfo()` function for boot banner
- Build timestamp macros

#### **include/EngineManager.h + src/EngineManager.cpp**
Single-engine lifecycle management:
- Power-On Self Test (POST) implementation
- Auto-start logic for RF Scanner
- Periodic health checks (5-second heartbeat)
- Engine creation and destruction

#### **include/SystemLogger.h + src/SystemLogger.cpp**
6-level logging system:
- **Levels:** INFORMATIONAL, WARNING, ERROR, CRITICAL, FLAGGED, SUCCESS
- Engine health tracking with heartbeat monitoring
- Log filtering (OLED shows only CRITICAL/FLAGGED/SUCCESS)
- Ring buffer (100 entries max)
- Timestamped entries (HH:MM:SS format)

#### **include/DisplayManager.h + src/DisplayManager.cpp** (OPTIMIZED in v1.1)
Split-screen OLED interface with font caching:
- **Left panel:** Engine health status (OK/ERR indicators)
- **Right panel:** Live critical logs with timestamps
- **Font caching:** `setFontCached()` reduces redundant calls (33% faster)
- **Boot sequence:** POST visualization with progress bar
- **Attack feedback:** Progress bars for deauth/PMKID/handshake operations

---

### Engine Files

#### **Engine: RF Scanner** (Main)

**include/RFScanner.h + src/RFScanner.cpp**
WiFi packet capture and attack engine:
- **Modes:** Passive monitoring, handshake capture, PMKID extraction, deauth attacks, beacon flooding
- **Integrations:**
  - PacketSniffer (promiscuous mode)
  - PMKIDCapture (clientless attacks)
  - CommandInterface (command execution)

**include/PacketSniffer.h + src/PacketSniffer.cpp**
WiFi promiscuous mode packet capture:
- **ISR-safe design:** Static members for interrupt context
- **Frame types:** Beacons, probe requests/responses, data, management, EAPOL
- **Channel hopping:** Scans channels 1-13
- **Device tracking:** MAC address resolution, RSSI, encryption type

**include/PMKIDCapture.h + src/PMKIDCapture.cpp**
Clientless PMKID extraction:
- **Passive PMKID:** Extracts from AP beacons
- **Active PMKID:** Sends association requests to trigger M1 frames
- **Hashcat export:** Mode 22000 format

---

### Command System (NEW in v1.1)

#### **include/CommandInterface.h + src/CommandInterface.cpp**
Dual-mode interactive command processor:
- **Serial CLI:** USB terminal at 115200 baud
- **Wireless C2:** Magic packet commands via WiFi
- **State machine:** 18 states (IDLE, SCANNING, AWAITING_TARGET, DEAUTH_ATTACK, etc.)
- **Session locking:** MAC-based authentication for wireless commands
- **Commands:** SCAN, DEAUTH, PMKID, HANDSHAKE, BEACONFLOOD, STATUS, HELP
- **Timeouts:** 2-minute session timeout, 60-second cooldown after attacks
- **Named constants:** `SESSION_TIMEOUT`, `SCAN_DURATION`, `ATTACK_DURATION`, etc.

**State Machine:**
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

#### **include/CommandLedger.h + src/CommandLedger.cpp**
Persistent state storage using LittleFS:
- Saves command state to filesystem
- Session MAC tracking
- Attack target persistence
- Survives reboots and crashes
- **Note:** Currently calls `save()` 13 times per operation (potential optimization)

---

### Utilities (NEW in v1.1)

#### **include/Utils.h** (v1.1 Optimization)
Unified MAC address utilities:
- **Zero heap allocations:** All operations use stack buffers
- **Functions:**
  - `macToString(mac, buf)` - Format MAC to string
  - `stringToMAC(str, mac)` - Parse string to MAC array
  - `macEquals(mac1, mac2)` - Compare two MACs
  - `isBroadcast(mac)` - Check for FF:FF:FF:FF:FF:FF
  - `isMulticast(mac)` - Check multicast bit
  - `isUnicast(mac)` - Check unicast
- **Eliminates:** 3 duplicate MAC formatting implementations from v1.0

---

## Build Artifacts

### Firmware Binaries (v1.1)

**firmware.bin** (852 KB, 43.3% of flash)
- Main application code
- All engine logic, command interface, and display rendering
- v1.1 optimizations included

**bootloader.bin** (17 KB)
- ESP32 first-stage bootloader
- Initializes hardware and loads application

**partitions.bin** (3 KB)
- Partition table defining flash memory layout
- Includes: bootloader, app0, nvs, littlefs

---

### Memory Usage (v1.1)

**Flash Memory**
- **Used:** 852,017 bytes (43.3% of 1,966,080 bytes)
- **Available:** 1,114,063 bytes (56.7% free)
- **Comparison to v1.0:** +0.7 KB (version strings and optimization code)

**RAM Usage (compile-time)**
- **Used:** 45,048 bytes (13.7% of 327,680 bytes)
- **Available:** 282,632 bytes (86.3% free)
- **Comparison to v1.0:** No change

**Performance (v1.1 vs v1.0)**
- Display rendering: 300µs → 200µs (33% faster)
- Font switches per frame: 6-8 → 2-3 (60% reduction)
- MAC formatting: String heap allocation → Stack buffer (zero heap)

---

## Development Workflow

### Building the Project

```bash
# Build v1.1 (default)
pio run

# Build v1.1 explicitly
pio run -e v1_1

# Build v1.1 debug
pio run -e v1_1_debug

# Build v1.0 (requires git checkout first)
git checkout v1.0
pio run -e v1_0
git checkout main

# Clean build
pio run --target clean
```

### Flashing to Device

```bash
# Upload v1.1 (recommended)
pio run -e v1_1 --target upload

# Upload and monitor
pio run -e v1_1 --target upload --target monitor

# Upload to specific port
pio run -e v1_1 --target upload --upload-port /dev/ttyUSB0

# Upload debug build
pio run -e v1_1_debug --target upload
```

### Monitoring

```bash
# Serial monitor
pio device monitor --baud 115200

# With exception decoder
pio device monitor --baud 115200 --filter esp32_exception_decoder

# With local echo (see typed commands)
pio device monitor --baud 115200 --echo
```

---

## File Organization Principles

### Header Files (include/)
- Class declarations
- Public API definitions
- Inline utility functions (Utils.h)
- Version constants (version.h)
- State machine enums (CommandInterface.h)

### Implementation Files (src/)
- Class method implementations
- Private helper functions
- Static member initialization

### Documentation (Docz/)
- User guides (QUICK_START.md)
- Attack tutorials (HANDSHAKE_CAPTURE_GUIDE.md, etc.)
- Architecture docs (LANGUAGE_ARCHITECTURE_REPORT.md)
- Command reference (COMMAND_INTERFACE_GUIDE.md)
- Optimization analysis (OPTIMIZATION_MASTER.md)

### Separation of Concerns
- **Engine:** RFScanner is self-contained (own .h and .cpp)
- **Commands:** CommandInterface handles both serial and wireless
- **State:** CommandLedger persists to filesystem
- **Display:** DisplayManager abstracts OLED rendering
- **Logging:** SystemLogger provides unified logging interface
- **Utilities:** Utils.h provides shared MAC operations

### Static Members
- **PacketSniffer:** Uses static members for ISR context
- **CommandInterface:** Static members for wireless packet callbacks
- **Required pattern:** ESP32 WiFi promiscuous mode callbacks run in ISR context

---

## Dependencies

### PlatformIO Libraries
- **U8g2 @ ^2.35.9** - OLED display driver (SSD1306)
  - Only external dependency
  - ~48 MB source code, ~30 KB in firmware

### ESP32 Built-in Libraries
- WiFi (WiFi connectivity and monitor mode)
- esp_wifi (Low-level WiFi API)
- esp_wifi_types (WiFi type definitions)
- LittleFS (Filesystem for state persistence)
- Wire (I2C communication for OLED)

### Removed Dependencies (v1.0 → v1.1)
- ❌ **ArduinoJson** - No longer needed (removed web/telnet/cloud features)
- **Result:** Freed 162 KB flash, 4 KB RAM

---

## v1.1 Optimizations

### Applied Optimizations (Safe, Zero-Risk)

1. **Font Caching** (DisplayManager.cpp)
   - Tracks `current_font` to avoid redundant `setFont()` calls
   - **Impact:** 33% faster display rendering (300µs → 200µs)
   - **Calls reduced:** 6-8 per frame → 2-3 per frame

2. **Unified MAC Utilities** (Utils.h)
   - Single implementation for MAC formatting/parsing
   - Stack buffers instead of heap-allocated Strings
   - **Impact:** Zero heap allocations, 3 duplicate implementations removed
   - **Used by:** CommandInterface, CommandLedger, DisplayManager

3. **Named Constants** (CommandInterface.cpp)
   - Magic numbers replaced with descriptive constants
   - **Examples:** `SESSION_TIMEOUT = 120000`, `SCAN_DURATION = 15000`
   - **Impact:** Improved code readability, self-documenting

### Deferred Optimizations (Medium/High-Risk)

See `Docz/OPTIMIZATION_MASTER.md` for:
- Batched filesystem saves (90% reduction in flash writes)
- Serial buffer optimization (zero allocations during typing)
- Display partial updates (70% less I2C traffic)
- Static packet buffers (eliminate dynamic allocation)

**These require debug toggles and extensive testing**, so they're deferred until a stable milestone.

---

## Version Control

### Git Tags
- **v1.1.0** - Current release (Nov 11, 2025)
- **v1.0.0** - Legacy pre-optimization release

### .gitignore Contents
```
.pio/
.vscode/
.platformio
*.bin
*.elf
*.o
*.swp
*.swo
*~
.DS_Store
```

### Files to Track
- All source files (src/, include/)
- Configuration files (platformio.ini, partitions.csv, config.h)
- Documentation (README.md, Docz/, BUILD_GUIDE.md, etc.)

### Files NOT to Track
- Build artifacts (.pio/build/)
- Library downloads (.pio/libdeps/)
- Python virtual environment (.pio/penv/)
- IDE settings (.vscode/, .idea/)
- Compiled binaries (*.bin, *.elf, *.o)

---

## Board-Specific Configuration

### Arduino Nano ESP32
- **Chip:** ESP32-S3
- **Flash:** 4 MB (uses 43.3%)
- **RAM:** 327 KB (uses 13.7%)
- **I2C Pins:**
  - SDA: A4 (GPIO 21)
  - SCL: A5 (GPIO 22)
- **USB:** CDC enabled for serial over USB
- **PSRAM:** Enabled for future expansion
- **Upload Port:** /dev/ttyACM0 (Linux), COM3 (Windows)

### ESP32 DevKit V1 (Alternative)
- **Chip:** ESP32-WROOM-32
- **Flash:** 4 MB
- **RAM:** 520 KB
- **I2C Pins:**
  - SDA: GPIO 21
  - SCL: GPIO 22
- **Upload Port:** /dev/ttyUSB0 (Linux), COM3 (Windows)

---

## Feature Comparison

### What Exists (v1.1.0)

✅ **Single-engine architecture** (RF Scanner)
✅ **WiFi monitor mode** (promiscuous packet capture)
✅ **Handshake capture** (WPA/WPA2 EAPOL M1-M4)
✅ **PMKID extraction** (passive + clientless attack)
✅ **Deauth attacks** (targeted + broadcast)
✅ **Beacon flooding** (fake AP creation)
✅ **Interactive command interface** (serial + wireless C2)
✅ **State machine** (18 states with session locking)
✅ **OLED display** (split-screen health + logs)
✅ **Hashcat export** (mode 22000 for both handshakes and PMKIDs)
✅ **Channel hopping** (scans all 13 WiFi channels)
✅ **Filesystem persistence** (LittleFS for command state)
✅ **Font caching** (33% faster display)
✅ **Unified utilities** (Utils.h for MAC operations)
✅ **Multi-environment builds** (v1_1, v1_1_debug, v1_0)

### What Does NOT Exist (Removed in v1.0)

❌ **NetworkAnalyzer engine** (removed for simplicity)
❌ **WebInterface** (HTTP server removed)
❌ **TelnetServer** (remote access removed)
❌ **CloudStorage** (WebDAV, S3, HTTP upload removed)
❌ **NetworkMonitor** (network quality metrics removed)
❌ **Dual-engine mode** (simplified to single RF Scanner)
❌ **ArduinoJson dependency** (no longer needed)

**Reason for removal:** Focus on WiFi attacks, reduce attack surface, simplify codebase

---

## Testing Utilities

### **test_i2c_scanner.cpp**
I2C device scanner for OLED troubleshooting:
- Scans I2C bus for connected devices
- Reports device addresses (typically 0x3C for SSD1306 OLED)
- Used for hardware debugging

**Compile separately:**
```bash
# Temporarily rename main.cpp
mv src/main.cpp src/main.cpp.backup

# Copy scanner as main
cp test_i2c_scanner.cpp src/main.cpp

# Build and upload
pio run --target upload

# Restore original main
mv src/main.cpp.backup src/main.cpp
```

---

## Build Configuration Details

### Build Flags (v1_1 environment)

```ini
build_flags =
    -DCORE_DEBUG_LEVEL=1          # Minimal logging
    -DCONFIG_BT_ENABLED=0          # Bluetooth disabled (saves 145KB)
    -DCONFIG_NIMBLE_ENABLED=0      # BLE disabled
    -DBOARD_HAS_PSRAM              # External RAM support
    -DARDUINO_USB_MODE=1           # USB CDC enabled
    -DARDUINO_USB_CDC_ON_BOOT=1    # Serial over USB
    -DVERSION_1_1=1                # Version flag
```

### Upload Configuration

```ini
upload_port = /dev/ttyACM0
upload_speed = 115200
upload_protocol = esptool
upload_flags =
    --before=no_reset_no_sync      # No auto-reset before upload
    --after=hard_reset             # Hard reset after upload
```

### Monitor Configuration

```ini
monitor_speed = 115200
monitor_filters = esp32_exception_decoder   # Decode crash stack traces
monitor_dtr = 0                              # Disable DTR
monitor_rts = 0                              # Disable RTS
```

---

## Documentation

See `Docz/README.md` for complete documentation index.

**Quick references:**
- **Quick Start:** `Docz/QUICK_START.md`
- **Build System:** `BUILD_GUIDE.md`
- **Commands:** `Docz/COMMAND_INTERFACE_GUIDE.md`
- **Attacks:** `Docz/HANDSHAKE_CAPTURE_GUIDE.md`, `Docz/PMKID_ATTACK_GUIDE.md`, etc.
- **Architecture:** `Docz/LANGUAGE_ARCHITECTURE_REPORT.md`
- **Optimizations:** `Docz/OPTIMIZATION_MASTER.md`

---

**Last Updated:** November 11, 2025
**Version:** v1.1.0
**Build System:** PlatformIO with multi-environment support
