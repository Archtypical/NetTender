#!/usr/bin/env python3
"""
Sniffy Tester Configuration
Centralized configuration for ESP32 testing tool
"""

# Network Interface Settings
DEFAULT_INTERFACE = None  # Auto-detect if None
DEFAULT_CHANNEL = 6        # 2.4GHz channel (1-14)
USE_MONITOR_MODE = True    # Must be True for Intel/most cards

# Serial Settings
DEFAULT_BAUDRATE = 115200
AUTO_DETECT_ESP32 = True

# Beacon Settings
DEFAULT_BEACON_INTERVAL = 0.1  # Seconds between beacons
DEFAULT_SSID = "ESP32_TEST"
GENERATE_RANDOM_MAC = True     # New MAC each run

# Test Modes
class TestMode:
    SIMPLE = "simple"           # Single MAC, continuous broadcast
    FLOOD = "flood"             # Multiple MACs to trigger [NEW DEVICE]
    INTEGRATED = "integrated"   # Broadcast + Serial monitoring

# Flood Mode Settings
FLOOD_COUNT = 20               # Number of unique MACs to send
FLOOD_INTERVAL = 1.0           # Seconds between each beacon

# Display Settings
VERBOSE = True
SHOW_STATS_INTERVAL = 5        # Seconds between stats updates

# ESP32 Detection
ESP32_KEYWORDS = ['CP210', 'CH340', 'USB Serial', 'UART', 'ttyUSB', 'ttyACM']

# Channel Hopping (for reference - not used in broadcast)
CHANNEL_HOP_INTERVAL = 1.0     # How often ESP32 should hop
CHANNELS_2_4GHZ = list(range(1, 14))  # 2.4GHz channels
