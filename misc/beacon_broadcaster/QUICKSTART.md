# Sniffy Tester - Quick Start

Ultra-condensed guide for testing ESP32 Sniffy.

## First Time Setup

```bash
cd /home/user/Projects/esp32/misc/beacon_broadcaster
./install.sh
```

## Every Time You Test

```bash
# Terminal 1: Create virtual monitor interface (WiFi stays connected!)
sudo ./monitor_mode.sh wlp0s20f3 setup

# Terminal 2: Run test (note: use 'wlp0s20f3mon' virtual interface)
sudo python3 sniffy_tester.py -s "TEST" -i wlp0s20f3mon --monitor

# When done: Remove virtual interface
sudo ./monitor_mode.sh wlp0s20f3 restore
```

## Test Modes

```bash
# Simple broadcast (use virtual interface 'wlp0s20f3mon')
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon -c 6

# Flood mode (20 unique MACs)
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon --flood -n 20

# With ESP32 monitoring
sudo python3 sniffy_tester.py -s "TestAP" -i wlp0s20f3mon --monitor
```

## Cleanup

```bash
# Emergency cleanup (kills all processes, restores WiFi)
sudo ./cleanup.sh
```

## Help

```bash
python3 sniffy_tester.py --help
```

---

See README.md for complete documentation.
