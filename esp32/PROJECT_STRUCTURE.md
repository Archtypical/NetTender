# ESP32 Multi-Engine Platform - Project Structure

## Pre-Build Structure

```
esp32/
├── include/                    # Header files
│   ├── CloudStorage.h         # Universal cloud storage protocols (WebDAV, S3, HTTP)
│   ├── config.h               # Operational mode configuration
│   ├── DataUploader.h         # Data upload management
│   ├── DisplayManager.h       # OLED display interface (SSD1306)
│   ├── EmergencyRouter.h      # Emergency router engine (Engine 3)
│   ├── EngineManager.h        # Multi-engine lifecycle manager
│   ├── NetworkAnalyzer.h      # Network analyzer engine (Engine 2)
│   ├── NetworkConfig.h        # Network feature flags
│   ├── NetworkMonitor.h       # Network quality and scan detection
│   ├── PacketSniffer.h        # WiFi promiscuous mode packet capture
│   ├── RFScanner.h            # RF scanner engine (Engine 1)
│   ├── SystemLogger.h         # Multi-level logging system
│   ├── TelnetServer.h         # Remote telnet access
│   └── WebInterface.h         # Web dashboard interface
│
├── src/                       # Implementation files
│   ├── CloudStorage.cpp       # Cloud storage implementation
│   ├── DisplayManager.cpp     # OLED display rendering
│   ├── EmergencyRouter.cpp    # Router engine implementation
│   ├── EngineManager.cpp      # Engine management logic
│   ├── main.cpp               # Application entry point
│   ├── NetworkAnalyzer.cpp    # Network analyzer implementation
│   ├── NetworkMonitor.cpp     # Network monitoring logic
│   ├── PacketSniffer.cpp      # Packet capture implementation
│   ├── RFScanner.cpp          # RF scanner implementation
│   ├── SystemLogger.cpp       # Logging system implementation
│   ├── TelnetServer.cpp       # Telnet server implementation
│   └── WebInterface.cpp       # Web server implementation
│
├── lib/                       # External libraries (empty, using PlatformIO registry)
├── platformio.ini             # PlatformIO build configuration
└── README.md                  # Project documentation
```

## Post-Build Structure

```
esp32/
├── [All pre-build files above]
│
├── .pio/                      # PlatformIO build system (generated)
│   ├── build/
│   │   └── esp32dev/
│   │       ├── firmware.elf      # ELF executable wit⎿  Wrote 288 lines to /home/user/esp32/PROJECT_STRUCTURE.md                                          
     # ESP32 Multi-Engine Platform - Project Structure

     ## Pre-Build Structure

     ```
     esp32/
     ├── include/                    # Header files
     │   ├── CloudStorage.h         # Universal cloud storage protocols (WebDAV, S3, HTTP)
     │   ├── config.h               # Operational mode configuration
     │   ├── DataUploader.h         # Data upload management
     │   ├── DisplayManager.h       # OLED display interface (SSD1306)
     │   ├── EmergencyRouter.h      # Emergency router engine (Engine 3)
     │   ├── EngineManager.h        # Multi-engine lifecycle manager
     │   ├── NetworkAnalyzer.h      # Network analyzer engine (Engine 2)
     │   ├── NetworkConfig.h        # Network feature flags
     │   ├── NetworkMonitor.h       # Network quality and scan detection
     │   ├── PacketSniffer.h        # WiFi promiscuous mode packet capture
     │   ├── RFScanner.h            # RF scanner engine (Engine 1)
     │   ├── SystemLogger.h         # Multi-level logging system
     │   ├── TelnetServer.h         # Remote telnet access
     │   └── WebInterface.h         # Web dashboard interface
     │
     ├── src/                       # Implementation files
     │   ├── CloudStorage.cpp       # Cloud storage implementation
     │   ├── DisplayManager.cpp     # OLED display rendering
     │   ├── EmergencyRouter.cpp    # Router engine implementation
     │   ├── EngineManager.cpp      # Engine management logic
     │   ├── main.cpp               # Application entry point
     │   ├── NetworkAnalyzer.cpp    # Network analyzer implementation
     │   ├── NetworkMonitor.cpp     # Network monitoring logic
     │   ├── PacketSniffer.cpp      # Packet capture implementation
     │   ├── RFScanner.cpp          # RF scanner implementation
     │   ├── SystemLogger.cpp       # Logging system implementation
     │   ├── TelnetServer.cpp       # Telnet server implementation
     │   └── WebInterface.cpp       # Web server implementation
     │
     ├── lib/                       # External libraries (empty, using PlatformIO registry)
     ├── platformio.ini             # PlatformIO build configuration
     └── README.md                  # Project documentation
     ```

     ## Post-Build Structure

     ```
     esp32/
     ├── [All pre-build files above]
     │
     ├── .pio/                      # PlatformIO build system (generated)
     │   ├── build/
     │   │   └── esp32dev/
     │   │       ├── firmware.elf      # ELF executable with debug symbols
     │   │       ├── firmware.bin      # Main application binary (943 KB)
     │   │       ├── bootloader.bin    # ESP32 bootloader (17 KB)
     │   │       ├── partitions.bin    # Partition table (3 KB)
     │   │       ├── src/              # Compiled object files (*.o)
     │   │       ├── lib*/             # Compiled library archives
     │   │       └── FrameworkArduino/ # Arduino framework objects
     │   │
     │   ├── libdeps/               # Downloaded library dependencies
     │   │   └── esp32dev/
     │   │       ├── U8g2/          # OLED display library
     │   │       ├── ArduinoJson/   # JSON parsing library
     │   │       └── [other libs]
     │   │
     │   └── penv/                  # Python virtual environment
     │
     └── .gitignore                 # Git ignore file (excludes .pio/)
     ```

     ## Key Files Description

     ### Configuration Files

     **platformio.ini**
     - Build system configuration
     - Board: ESP32 Dev Module
     - Framework: Arduino
     - Libraries: U8g2, ArduinoJson, WiFi, HTTPClient, etc.
     - Build flags: -fno-rtti (disable RTTI for memory savings)

     **include/config.h**
     - Operational mode selection (Dual Engine vs Emergency Router)
     - Auto-start configuration
     - Boot sequence options
     - POST (Power-On Self Test) enable/disable

     **include/NetworkConfig.h**
     - Comprehensive network feature flags
     - Cloud storage protocol configuration
     - Service enable/disable toggles

     ### Core System Files

     **src/main.cpp**
     - Application entry point
     - System initialization
     - Main loop coordination
     - WiFi management

     **include/EngineManager.h + src/EngineManager.cpp**
     - Multi-engine lifecycle management
     - Power-On Self Test (POST) implementation
     - Auto-start logic for dual-engine or router mode
     - Periodic health checks
     - Engine creation and destruction

     **include/SystemLogger.h + src/SystemLogger.cpp**
     - Multi-level logging (INFORMATIONAL, WARNING, ERROR, CRITICAL, FLAGGED, SUCCESS)
     - Engine health tracking with heartbeat monitoring
     - Log filtering for OLED display
     - Web dashboard log export

     **include/DisplayManager.h + src/DisplayManager.cpp**
     - Split-screen OLED interface (64 pixels left, 64 pixels right)
     - Left: Engine health status with OK/ERR/!! indicators
     - Right: Live critical logs with timestamps
     - Boot sequence visualization

     ### Engine Files

     **Engine 1: RF Scanner**
     - include/RFScanner.h + src/RFScanner.cpp
     - include/PacketSniffer.h + src/PacketSniffer.cpp
     - Modes: Passive scan, deauth attack, beacon spam, probe flood, evil twin, PMKID capture, BLE scan
     - WiFi promiscuous mode packet capture

     **Engine 2: Network Analyzer**
     - include/NetworkAnalyzer.h + src/NetworkAnalyzer.cpp
     - include/NetworkMonitor.h + src/NetworkMonitor.cpp
     - Modes: Passive monitor, DNS server, MITM proxy, traffic analysis, flow capture, network map
     - ARP spoofing, DNS blocking, packet inspection

     **Engine 3: Emergency Router**
     - include/EmergencyRouter.h + src/EmergencyRouter.cpp
     - Converts phone hotspot to WiFi router
     - Dual WiFi mode (STA + AP)
     - DHCP server, DNS forwarding, client tracking

     ### Network Services

     **include/WebInterface.h + src/WebInterface.cpp**
     - HTTP server on port 80
     - Dashboard with engine status
     - Log viewer with color-coded entries
     - RESTful API for programmatic access

     **include/TelnetServer.h + src/TelnetServer.cpp**
     - Telnet server on port 23
     - Remote command-line interface
     - Commands: status, engines, start, stop, restart, help, clear, exit

     **include/CloudStorage.h + src/CloudStorage.cpp**
     - Universal cloud storage protocols
     - WebDAV support (NextCloud, ownCloud, Google Drive, etc.)
     - S3-compatible storage (AWS S3, MinIO, Wasabi, etc.)
     - Generic HTTP POST/PUT for custom endpoints

     ## Build Artifacts

h debug symbols
│   │       ├── firmware.bin      # Main application binary (943 KB)
│   │       ├── bootloader.bin    # ESP32 bootloader (17 KB)
│   │       ├── partitions.bin    # Partition table (3 KB)
│   │       ├── src/              # Compiled object files (*.o)
│   │       ├── lib*/             # Compiled library archives
│   │       └── FrameworkArduino/ # Arduino framework objects
│   │
│   ├── libdeps/               # Downloaded library dependencies
│   │   └── esp32dev/
│   │       ├── U8g2/          # OLED display library
│   │       ├── ArduinoJson/   # JSON parsing library
│   │       └── [other libs]
│   │
│   └── penv/                  # Python virtual environment
│
└── .gitignore                 # Git ignore file (excludes .pio/)
```

## Key Files Description

### Configuration Files

**platformio.ini**
- Build system configuration
- Board: ESP32 Dev Module
- Framework: Arduino
- Libraries: U8g2, ArduinoJson, WiFi, HTTPClient, etc.
- Build flags: -fno-rtti (disable RTTI for memory savings)

**include/config.h**
- Operational mode selection (Dual Engine vs Emergency Router)
- Auto-start configuration
- Boot sequence options
- POST (Power-On Self Test) enable/disable

**include/NetworkConfig.h**
- Comprehensive network feature flags
- Cloud storage protocol configuration
- Service enable/disable toggles

### Core System Files

**src/main.cpp**
- Application entry point
- System initialization
- Main loop coordination
- WiFi management

**include/EngineManager.h + src/EngineManager.cpp**
- Multi-engine lifecycle management
- Power-On Self Test (POST) implementation
- Auto-start logic for dual-engine or router mode
- Periodic health checks
- Engine creation and destruction

**include/SystemLogger.h + src/SystemLogger.cpp**
- Multi-level logging (INFORMATIONAL, WARNING, ERROR, CRITICAL, FLAGGED, SUCCESS)
- Engine health tracking with heartbeat monitoring
- Log filtering for OLED display
- Web dashboard log export

**include/DisplayManager.h + src/DisplayManager.cpp**
- Split-screen OLED interface (64 pixels left, 64 pixels right)
- Left: Engine health status with OK/ERR/!! indicators
- Right: Live critical logs with timestamps
- Boot sequence visualization

### Engine Files

**Engine 1: RF Scanner**
- include/RFScanner.h + src/RFScanner.cpp
- include/PacketSniffer.h + src/PacketSniffer.cpp
- Modes: Passive scan, deauth attack, beacon spam, probe flood, evil twin, PMKID capture, BLE scan
- WiFi promiscuous mode packet capture

**Engine 2: Network Analyzer**
- include/NetworkAnalyzer.h + src/NetworkAnalyzer.cpp
- include/NetworkMonitor.h + src/NetworkMonitor.cpp
- Modes: Passive monitor, DNS server, MITM proxy, traffic analysis, flow capture, network map
- ARP spoofing, DNS blocking, packet inspection

**Engine 3: Emergency Router**
- include/EmergencyRouter.h + src/EmergencyRouter.cpp
- Converts phone hotspot to WiFi router
- Dual WiFi mode (STA + AP)
- DHCP server, DNS forwarding, client tracking

### Network Services

**include/WebInterface.h + src/WebInterface.cpp**
- HTTP server on port 80
- Dashboard with engine status
- Log viewer with color-coded entries
- RESTful API for programmatic access

**include/TelnetServer.h + src/TelnetServer.cpp**
- Telnet server on port 23
- Remote command-line interface
- Commands: status, engines, start, stop, restart, help, clear, exit

**include/CloudStorage.h + src/CloudStorage.cpp**
- Universal cloud storage protocols
- WebDAV support (NextCloud, ownCloud, Google Drive, etc.)
- S3-compatible storage (AWS S3, MinIO, Wasabi, etc.)
- Generic HTTP POST/PUT for custom endpoints

## Build Artifacts

### Firmware Binaries

**firmware.bin** (943,952 bytes)
- Main application code
- Flash usage: 71.5% of 1,310,720 bytes partition
- Contains all engine logic, network services, and UI

**bootloader.bin** (17,536 bytes)
- ESP32 first-stage bootloader
- Initializes hardware and loads application

**partitions.bin** (3,072 bytes)
- Partition table defining flash memory layout
- Typically includes: bootloader, app0, nvs, spiffs

### Memory Usage

**Flash Memory**
- Used: 937,369 bytes (71.5%)
- Available: 373,351 bytes (28.5%)
- Total: 1,310,720 bytes

**RAM Usage (at compile time)**
- Used: 49,968 bytes (15.2%)
- Available: 277,712 bytes (84.8%)
- Total: 327,680 bytes

## Development Workflow

### Building the Project

```bashu8g2
# Clean build
~/.platformio/penv/bin/platformio run --target clean

# Build firmware
~/.platformio/penv/bin/platformio run

# Build with verbose output
~/.platformio/penv/bin/platformio run -v
```

### Flashing to Device

```bash
# Auto-detect port and flash
~/.platformio/penv/bin/platformio run --target upload

# Specify port manually
~/.platformio/penv/bin/platformio run --target upload --upload-port /dev/ttyUSB0

# Flash and monitor serial output
~/.platformio/penv/bin/platformio run --target upload --target monitor
```

### Monitoring

```bash
# Serial monitor
~/.platformio/penv/bin/platformio device monitor

# Serial monitor with custom baud rate
~/.platformio/penv/bin/platformio device monitor --baud 115200
```

## File Organization Principles

### Header Files (include/)
- All class declarations
- Public API definitions
- Constant definitions
- Struct definitions

### Implementation Files (src/)
- Class method implementations
- Private helper functions
- Static member initialization

### Separation of Concerns
- Each engine is self-contained (own .h and .cpp)
- Network services are independent modules
- Configuration is centralized in config.h and NetworkConfig.h
- Logging is abstracted through SystemLogger

### Static Members
- PacketSniffer uses static members for ISR context
- Enables hardware callback access to packet processing state
- Required pattern for ESP32 WiFi promiscuous mode

## Dependencies

### PlatformIO Libraries
- U8g2 @ 2.36.15 (OLED display driver)
- ArduinoJson @ 6.21.5 (JSON parsing)
- WiFi @ 2.0.0 (ESP32 WiFi)
- HTTPClient @ 2.0.0 (HTTP requests)
- WiFiClientSecure @ 2.0.0 (HTTPS)
- DNSServer @ 2.0.0 (DNS server)
- ESPmDNS @ 2.0.0 (mDNS responder)
- WebServer @ 2.0.0 (HTTP server)
- Wire @ 2.0.0 (I2C communication)

### ESP-IDF Components
- esp_wifi (WiFi low-level API)
- esp_wifi_types (WiFi type definitions)

## Version Control

### .gitignore Recommendations
```
.pio/
.vscode/
.platformio
*.bin
*.elf
*.o
```

### Files to Track
- All source files (src/, include/)
- Configuration files (platformio.ini, config.h, NetworkConfig.h)
- Documentation (README.md, PROJECT_STRUCTURE.md)

### Files NOT to Track
- Build artifacts (.pio/build/)
- Library downloads (.pio/libdeps/)
- Python virtual environment (.pio/penv/)
- IDE settings (.vscode/, .idea/)
