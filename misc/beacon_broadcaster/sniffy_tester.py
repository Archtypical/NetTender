#!/usr/bin/env python3
"""
Sniffy Tester - ESP32 WiFi Testing Tool
Broadcasts beacons and monitors ESP32 serial output

Usage:
    # Simple beacon broadcast
    sudo python3 sniffy_tester.py -s "TestAP" -c 6

    # With ESP32 monitoring
    sudo python3 sniffy_tester.py -s "TestAP" --monitor

    # Flood mode (unique MACs)
    sudo python3 sniffy_tester.py -s "TestAP" --flood -n 20

    # Full integrated test
    sudo python3 sniffy_tester.py -s "TestAP" --monitor --serial /dev/ttyACM0
"""

import argparse
import sys
import time
import os
import random
import threading
import queue
from datetime import datetime

# Check root early
if os.geteuid() != 0:
    print("[!] ERROR: Must run as root")
    print("[!] Usage: sudo python3 sniffy_tester.py -s \"TestAP\"")
    sys.exit(1)

try:
    from scapy.all import RadioTap, Dot11, Dot11Beacon, Dot11Elt, sendp, conf
except ImportError:
    print("[!] ERROR: scapy not installed")
    print("[!] Run: sudo python3 -m pip install scapy pyserial")
    sys.exit(1)

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

import config

# ============================================================================
# Core Functions
# ============================================================================

def generate_random_mac():
    """Generate a random locally-administered MAC address."""
    first = (random.randint(0, 255) & 0xFE) | 0x02
    rest = [random.randint(0, 255) for _ in range(5)]
    return '%02x:%s' % (first, ':'.join('%02x' % b for b in rest))

def validate_mac(mac):
    """Validate MAC address format."""
    parts = mac.split(':')
    if len(parts) != 6:
        return False
    try:
        return all(0 <= int(part, 16) <= 255 for part in parts)
    except ValueError:
        return False

def create_beacon_frame(ssid, bssid, channel=6, encrypted=True):
    """Create 802.11 beacon frame."""
    dot11 = Dot11(
        type=0, subtype=8,
        addr1='ff:ff:ff:ff:ff:ff',
        addr2=bssid,
        addr3=bssid
    )

    beacon = Dot11Beacon(
        cap='ESS+privacy' if encrypted else 'ESS',
        timestamp=int(time.time() * 1000000)
    )

    essid = Dot11Elt(ID='SSID', info=ssid.encode(), len=len(ssid))
    rates = Dot11Elt(ID='Rates', info=b'\x82\x84\x8b\x96\x24\x30\x48\x6c')
    dsset = Dot11Elt(ID='DSset', info=bytes([channel]))
    tim = Dot11Elt(ID='TIM', info=b'\x00\x01\x00\x00')
    ext_rates = Dot11Elt(ID='ESRates', info=b'\x0c\x12\x18\x60')

    return RadioTap() / dot11 / beacon / essid / rates / dsset / tim / ext_rates

# ============================================================================
# Serial Monitor (Optional)
# ============================================================================

class SerialMonitor:
    """Monitor ESP32 serial output in background thread."""

    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.thread = None
        self.queue = queue.Queue()
        self.stats = {'beacons_detected': 0, 'new_devices': 0, 'deauths': 0}

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            print(f"[SERIAL] Connected to {self.port}")
            return True
        except Exception as e:
            print(f"[SERIAL] Error: {e}")
            return False

    def start(self):
        if not self.connect():
            return False
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.serial:
            self.serial.close()

    def _monitor_loop(self):
        while self.running:
            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.queue.put(line)
                        self._parse_line(line)
            except Exception:
                time.sleep(0.1)

    def _parse_line(self, line):
        line_lower = line.lower()
        if 'beacon' in line_lower:
            self.stats['beacons_detected'] += 1
        if '[new device]' in line_lower:
            self.stats['new_devices'] += 1
        if 'deauth' in line_lower:
            self.stats['deauths'] += 1

    def get_lines(self, max_lines=10):
        lines = []
        try:
            while len(lines) < max_lines:
                lines.append(self.queue.get_nowait())
        except queue.Empty:
            pass
        return lines

def find_esp32_port():
    """Auto-detect ESP32 serial port."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc_lower = port.description.lower()
        dev_lower = port.device.lower()
        for keyword in config.ESP32_KEYWORDS:
            if keyword.lower() in desc_lower or keyword.lower() in dev_lower:
                return port.device
    if ports:
        return ports[0].device
    return None

# ============================================================================
# Test Modes
# ============================================================================

def simple_broadcast(interface, ssid, mac, channel, interval, encrypted):
    """Simple continuous broadcast with single MAC."""
    print(f"\n{'='*60}")
    print(f"SIMPLE BROADCAST MODE")
    print(f"{'='*60}")
    print(f"Interface: {interface}")
    print(f"SSID:      {ssid}")
    print(f"MAC:       {mac}")
    print(f"Channel:   {channel}")
    print(f"Interval:  {interval}s")
    print(f"Security:  {'Encrypted' if encrypted else 'Open'}")
    print(f"{'='*60}\n")

    conf.iface = interface
    frame = create_beacon_frame(ssid, mac, channel, encrypted)

    sent = 0
    start_time = time.time()

    try:
        while True:
            sendp(frame, iface=interface, verbose=False)
            sent += 1

            if sent % 10 == 0:
                elapsed = time.time() - start_time
                rate = sent / elapsed if elapsed > 0 else 0
                print(f"\r[*] Beacons: {sent} | Rate: {rate:.1f}/s", end='', flush=True)

            time.sleep(interval)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n[+] Stopped. Sent {sent} beacons in {elapsed:.1f}s ({sent/elapsed:.1f}/s)")

def flood_broadcast(interface, ssid, channel, count, interval, encrypted):
    """Flood mode - send beacons with unique MACs."""
    print(f"\n{'='*60}")
    print(f"FLOOD MODE - Unique MACs")
    print(f"{'='*60}")
    print(f"Interface: {interface}")
    print(f"SSID:      {ssid}")
    print(f"Channel:   {channel}")
    print(f"Count:     {count} unique MACs")
    print(f"Interval:  {interval}s between beacons")
    print(f"{'='*60}\n")
    print("[*] Each beacon uses a different MAC to trigger ESP32 [NEW DEVICE]\n")

    conf.iface = interface

    for i in range(count):
        mac = generate_random_mac()
        frame = create_beacon_frame(ssid, mac, channel, encrypted)
        sendp(frame, iface=interface, verbose=False)

        print(f"[{i+1}/{count}] Sent from MAC: {mac}")
        time.sleep(interval)

    print(f"\n[+] Flood complete! Sent {count} beacons with unique MACs")

def integrated_test(interface, ssid, mac, channel, interval, encrypted, serial_port, baudrate):
    """Integrated mode - broadcast + ESP32 serial monitoring."""
    print(f"\n{'='*60}")
    print(f"INTEGRATED TEST MODE")
    print(f"{'='*60}\n")

    # Setup serial monitor
    monitor = None
    if SERIAL_AVAILABLE and serial_port:
        monitor = SerialMonitor(serial_port, baudrate)
        if not monitor.start():
            print("[!] Serial monitoring failed, continuing broadcast-only")
            monitor = None

    # Setup broadcast
    conf.iface = interface
    frame = create_beacon_frame(ssid, mac, channel, encrypted)

    print(f"{'='*60}")
    print(f"Broadcasting: {ssid} on CH{channel} | MAC: {mac}")
    if monitor:
        print(f"Monitoring:   {serial_port} @ {baudrate} baud")
    print(f"{'='*60}\n")

    if monitor:
        print("┌─ ESP32 SERIAL OUTPUT " + "─"*37 + "┐")

    sent = 0
    start_time = time.time()
    last_stats = time.time()

    try:
        while True:
            sendp(frame, iface=interface, verbose=False)
            sent += 1

            if monitor:
                lines = monitor.get_lines(5)
                for line in lines:
                    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    if ssid in line:
                        print(f"│ [{ts}] \033[92m{line}\033[0m")  # Green highlight
                    else:
                        print(f"│ [{ts}] {line}")

            if time.time() - last_stats >= config.SHOW_STATS_INTERVAL:
                elapsed = time.time() - start_time
                rate = sent / elapsed if elapsed > 0 else 0
                if monitor:
                    print("├" + "─"*59 + "┤")
                    print(f"│ Stats: Beacons: {sent} ({rate:.1f}/s) | Detected: {monitor.stats['new_devices']} | Deauths: {monitor.stats['deauths']}" + " "*(60-len(f"Stats: Beacons: {sent} ({rate:.1f}/s) | Detected: {monitor.stats['new_devices']} | Deauths: {monitor.stats['deauths']}")) + "│")
                    print("├" + "─"*59 + "┤")
                else:
                    print(f"\r[*] Beacons: {sent} | Rate: {rate:.1f}/s", end='', flush=True)
                last_stats = time.time()

            time.sleep(interval)

    except KeyboardInterrupt:
        if monitor:
            print("\n└" + "─"*59 + "┘\n")
        elapsed = time.time() - start_time
        print(f"\n[+] Test complete!")
        print(f"[+] Runtime:  {elapsed:.1f}s")
        print(f"[+] Beacons:  {sent} ({sent/elapsed:.1f}/s)")
        if monitor:
            print(f"[+] ESP32 detected {monitor.stats['new_devices']} new devices")
            monitor.stop()

# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Sniffy Tester - ESP32 WiFi Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple broadcast
  sudo python3 sniffy_tester.py -s "TestAP" -c 6

  # Flood mode (20 unique MACs)
  sudo python3 sniffy_tester.py -s "TestAP" --flood -n 20

  # Monitor ESP32 while broadcasting
  sudo python3 sniffy_tester.py -s "TestAP" --monitor

  # Full integrated test
  sudo python3 sniffy_tester.py -s "TestAP" --monitor --serial /dev/ttyACM0
        """
    )

    parser.add_argument('-s', '--ssid', required=True, help='SSID to broadcast')
    parser.add_argument('-c', '--channel', type=int, default=config.DEFAULT_CHANNEL,
                        help=f'Channel 1-14 (default: {config.DEFAULT_CHANNEL})')
    parser.add_argument('-i', '--interface', default=None,
                        help='Monitor interface (e.g., wlp0s20f3mon - virtual interface)')
    parser.add_argument('-m', '--mac', default=None,
                        help='MAC address (random if not specified)')
    parser.add_argument('-t', '--interval', type=float, default=config.DEFAULT_BEACON_INTERVAL,
                        help=f'Beacon interval in seconds (default: {config.DEFAULT_BEACON_INTERVAL})')
    parser.add_argument('--open', action='store_true',
                        help='Broadcast as open network (default: encrypted)')

    # Test modes
    parser.add_argument('--flood', action='store_true',
                        help='Flood mode: send beacons with unique MACs')
    parser.add_argument('-n', '--count', type=int, default=config.FLOOD_COUNT,
                        help=f'Flood mode: number of unique MACs (default: {config.FLOOD_COUNT})')
    parser.add_argument('--monitor', action='store_true',
                        help='Monitor ESP32 serial output')

    # Serial options
    parser.add_argument('--serial', default=None,
                        help='ESP32 serial port (auto-detect if not specified)')
    parser.add_argument('--baudrate', type=int, default=config.DEFAULT_BAUDRATE,
                        help=f'Serial baudrate (default: {config.DEFAULT_BAUDRATE})')

    args = parser.parse_args()

    # Validate inputs
    if len(args.ssid) > 32:
        print("[!] ERROR: SSID must be ≤32 characters")
        sys.exit(1)

    if not 1 <= args.channel <= 14:
        print("[!] ERROR: Channel must be 1-14 (2.4GHz only)")
        sys.exit(1)

    if args.mac and not validate_mac(args.mac):
        print("[!] ERROR: Invalid MAC format (use AA:BB:CC:DD:EE:FF)")
        sys.exit(1)

    # Get interface
    interface = args.interface
    if not interface:
        print("[!] ERROR: Must specify interface with -i")
        print("[!] Hint: Use 'iw dev' to list interfaces")
        print("[!] Example: sudo python3 sniffy_tester.py -s \"TestAP\" -i wlp0s20f3mon")
        sys.exit(1)

    # Generate MAC if needed
    mac = args.mac if args.mac else generate_random_mac()
    if not args.mac:
        print(f"[*] Generated random MAC: {mac}")

    # Determine mode and run
    try:
        if args.flood:
            flood_broadcast(
                interface, args.ssid, args.channel,
                args.count, args.interval, not args.open
            )
        elif args.monitor:
            # Integrated mode
            serial_port = args.serial
            if not serial_port and SERIAL_AVAILABLE:
                serial_port = find_esp32_port()
                if serial_port:
                    print(f"[*] Auto-detected ESP32: {serial_port}")

            integrated_test(
                interface, args.ssid, mac, args.channel,
                args.interval, not args.open, serial_port, args.baudrate
            )
        else:
            # Simple mode
            simple_broadcast(
                interface, args.ssid, mac, args.channel,
                args.interval, not args.open
            )

    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
