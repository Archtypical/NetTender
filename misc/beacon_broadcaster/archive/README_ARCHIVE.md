# Archive - Old Beacon Broadcaster Files

This folder contains the original/experimental beacon broadcaster scripts that have been replaced by the streamlined `sniffy_tester.py` module.

## Archived Files

### Original Scripts
- `beacon_broadcast.py` - Standalone broadcaster with virtual NIC support (didn't work on Intel cards)
- `integrated_test.py` - Original integrated testing script
- `flood_test.py` - Original flood mode script

### Setup Scripts
- `setup.sh` - Original setup script
- `setup_monitor.sh` - Monitor mode setup (replaced by `monitor_mode.sh`)
- `restore_wifi.sh` - WiFi restore (now in `monitor_mode.sh restore`)
- `cleanup.sh` - Cleanup script (integrated into `monitor_mode.sh`)
- `install_deps.sh` - Dependency installer (replaced by `install.sh`)

### Testing/Debug
- `test_setup.sh` - Setup verification script
- `test_esp32.sh` - ESP32 integration test
- `debug_broadcast.sh` - Debug helper

### Documentation
- `TROUBLESHOOTING.md` - Old troubleshooting guide (merged into main README)

## Why Archived?

These files were replaced because:

1. **Virtual NIC approach didn't work** on Intel wireless cards (wlp0s20f3)
2. **Too many files** with overlapping functionality
3. **Confusing workflow** - unclear which script to use when
4. **Scattered configuration** - settings spread across multiple files

## New Streamlined Approach

Everything is now consolidated into:

- `sniffy_tester.py` - Unified tool (all modes in one script)
- `config.py` - Centralized configuration
- `monitor_mode.sh` - Monitor mode management
- `install.sh` - Simple installation
- `README.md` - Clear documentation

## If You Need These Files

They're preserved here for reference. The new `sniffy_tester.py` includes all the functionality:

| Old Script | New Equivalent |
|-----------|----------------|
| `beacon_broadcast.py -s "Test"` | `sniffy_tester.py -s "Test" -i wlp0s20f3` |
| `integrated_test.py -s "Test"` | `sniffy_tester.py -s "Test" -i wlp0s20f3 --monitor` |
| `flood_test.py -s "Test" -n 20` | `sniffy_tester.py -s "Test" -i wlp0s20f3 --flood -n 20` |
| `setup_monitor.sh wlp0s20f3` | `monitor_mode.sh wlp0s20f3 setup` |
| `restore_wifi.sh wlp0s20f3` | `monitor_mode.sh wlp0s20f3 restore` |

---

*Archived: 2025-11-10*
