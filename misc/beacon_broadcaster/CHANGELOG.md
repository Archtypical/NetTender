# Changelog - Beacon Broadcaster

## Version 1.1 (2025-11-11)

### Major Architecture Change: Virtual Monitor Interface Implementation

**Problem Solved:**
The original scripts converted the physical wireless adapter to monitor mode, which:
- Disconnected WiFi completely
- Required NetworkManager to be stopped
- Could leave the system in a broken network state if not properly restored

**New Solution:**
All scripts now create a **virtual monitor interface** that runs alongside the physical adapter:
- Physical adapter stays in managed mode with WiFi connected
- Virtual interface (e.g., `wlp0s20f3mon`) operates in monitor mode
- No WiFi disconnection during testing
- NetworkManager stays running
- Safe and reversible operations

---

## Files Modified

### Core Scripts

#### 1. `monitor_mode.sh` (Lines 65-176)
**Before:**
- Stopped NetworkManager
- Converted physical interface to monitor mode
- Disconnected WiFi

**After:**
- Creates virtual monitor interface using `iw dev <phy> interface add <name>mon type monitor`
- Physical interface remains unchanged
- Instructs NetworkManager to ignore virtual interface
- WiFi connectivity preserved

#### 2. `cleanup.sh` (Lines 76-131)
**Before:**
- Removed all monitor interfaces indiscriminately
- Always restarted NetworkManager
- Could affect physical adapters

**After:**
- Identifies and removes only **virtual** monitor interfaces (ending with 'mon')
- Checks if physical interfaces are stuck in monitor mode
- Only restarts NetworkManager if physical interfaces were affected
- Smart detection prevents unnecessary network disruption

### Documentation Files

#### 3. `README.md` (Multiple sections)
**Updated:**
- Quick Start section: Changed "Enable monitor mode" → "Create virtual monitor interface"
- All command examples now use `wlp0s20f3mon` (virtual interface)
- Added new comparison table: "Virtual Monitor Interface Benefits"
- Updated troubleshooting section with network adapter recovery steps
- Added note about WiFi staying connected

**Key sections updated:**
- Lines 38-65: Quick Start
- Lines 69-125: Usage Examples
- Lines 154-207: Typical Testing Workflow
- Lines 233-262: Troubleshooting
- Lines 331-345: Technical Details

#### 4. `QUICKSTART.md` (Lines 12-36)
**Updated:**
- All interface references changed from `wlp0s20f3` to `wlp0s20f3mon`
- Added note: "WiFi stays connected!"
- Updated all example commands

#### 5. `MODULE_INFO.md` (Comprehensive rewrite)
**Updated:**
- Version bumped to 1.1
- Added v1.1 changelog
- Completely rewrote "Design Decisions" section
  - **Before:** "Why Not Virtual Interfaces?" (claimed they abandoned this approach)
  - **After:** "Why Virtual Interfaces?" (explains the new implementation)
- Updated all monitor mode descriptions
- Updated all command examples
- Updated testing scenarios

**Key sections rewritten:**
- Lines 3-12: Version and changelog
- Lines 48-61: Monitor Mode Manager description
- Lines 72-80: Cleanup Utility description
- Lines 92-114: Usage Workflow
- Lines 184-203: Design Decisions
- Lines 226-253: Testing Scenarios

#### 6. `install.sh` (Lines 116-127)
**Updated:**
- Quick Start instructions now mention virtual interface
- Example commands use `wlp0s20f3mon` instead of `wlp0s20f3`
- Added clarifying note about WiFi staying connected

#### 7. `sniffy_tester.py` (Lines 337, 379)
**Updated:**
- Help text for `-i/--interface` argument updated to show `wlp0s20f3mon` example
- Error message example updated to use virtual interface name

### Configuration Files

#### 8. `requirements.txt` - No changes needed
- Dependencies remain the same

#### 9. `config.py` - No changes needed
- Configuration settings remain the same

---

## Usage Changes

### Old Workflow (v1.0)
```bash
# Stopped NetworkManager, disconnected WiFi
sudo ./monitor_mode.sh wlp0s20f3 setup

# Used physical interface (now in monitor mode)
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3

# Restored managed mode, restarted NetworkManager
sudo ./monitor_mode.sh wlp0s20f3 restore
```

### New Workflow (v1.1)
```bash
# Creates virtual interface, WiFi stays connected!
sudo ./monitor_mode.sh wlp0s20f3 setup

# Use VIRTUAL interface (physical stays connected)
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon

# Removes virtual interface, physical unchanged
sudo ./monitor_mode.sh wlp0s20f3 restore
```

---

## Technical Details

### Virtual Interface Creation
```bash
# Create virtual monitor interface
iw dev wlp0s20f3 interface add wlp0s20f3mon type monitor

# Bring it up
ip link set wlp0s20f3mon up

# Tell NetworkManager to ignore it
nmcli device set wlp0s20f3mon managed no
```

### Virtual Interface Removal
```bash
# Bring down virtual interface
ip link set wlp0s20f3mon down

# Delete virtual interface
iw dev wlp0s20f3mon del
```

### Benefits
1. **No WiFi disconnection** - Physical adapter stays connected
2. **No NetworkManager restart** - Service keeps running
3. **Safe operations** - Virtual interfaces can be created/removed without risk
4. **Unique MAC addresses** - Virtual interface gets its own MAC
5. **Easy recovery** - `./cleanup.sh` can fix any issues

### Compatibility
- Requires wireless driver with virtual interface support (mac80211-based)
- Works with Intel, Atheros, Realtek chipsets
- Check support: `iw phy` shows capabilities

---

## Migration Notes

If you're upgrading from v1.0:

1. **Update your commands** - Use `wlp0s20f3mon` (virtual interface) instead of `wlp0s20f3`
2. **Check your scripts** - Any automation should reference the virtual interface
3. **Run cleanup** - If you have leftover monitor mode configs:
   ```bash
   sudo ./cleanup.sh
   ```

---

## Files NOT Modified

- `archive/*` - Archived/deprecated files left as-is
- Python cache files - Managed by cleanup script
- Git repository files - Not affected

---

## Troubleshooting New Issues

### "Interface wlp0s20f3mon doesn't exist"
**Solution:** Run setup first to create the virtual interface
```bash
sudo ./monitor_mode.sh wlp0s20f3 setup
```

### "Virtual interface creation failed"
**Solution:** Your wireless driver may not support virtual interfaces
- Check capabilities: `iw list | grep -A 10 "valid interface combinations"`
- Fallback: Use v1.0 scripts from archive (disconnects WiFi)

### "NetworkManager managing monitor interface"
**Solution:** This shouldn't happen, but if it does:
```bash
sudo nmcli device set wlp0s20f3mon managed no
```

### Network adapter in weird state
**Solution:** Run comprehensive cleanup
```bash
sudo ./cleanup.sh
```

---

## Credits

**Issue:** Network adapters in broken state after running original scripts
**Reporter:** User
**Resolution:** Complete rewrite to virtual interface architecture
**Date:** 2025-11-11
