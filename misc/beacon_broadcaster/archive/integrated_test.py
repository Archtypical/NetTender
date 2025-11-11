#!/usr/bin/env python3
"""
Integrated ESP32 Testing Tool
Broadcasts WiFi beacons while simultaneously monitoring ESP32 serial output.

This demonstrates that virtual NIC creation doesn't disrupt other connections!
"""

import argparse
import sys
import time
import threading
import queue
import re
from datetime import datetime
from scapy.all import RadioTap, Dot11, Dot11Beacon, Dot11Elt, sendp, conf
import serial
import serial.tools.list_ports

# Import from our beacon broadcaster
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from beacon_broadcast import (
    VirtualInterface,
    generate_random_mac,
    create_beacon_frame,
    validate_mac
)

class SerialMonitor:
    """Monitors ESP32 serial output in a separate thread."""

    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.thread = None
        self.queue = queue.Queue()
        self.stats = {
            'beacons_detected': 0,
            'packets_captured': 0,
            'handshakes': 0,
            'deauths': 0
        }

    def connect(self):
        """Connect to ESP32 serial port."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            time.sleep(2)  # Wait for ESP32 to reset
            print(f"[SERIAL] Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"[SERIAL] Error: {e}")
            return False

    def start(self):
        """Start monitoring in background thread."""
        if not self.serial:
            if not self.connect():
                return False

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        """Stop monitoring."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.serial:
            self.serial.close()

    def _monitor_loop(self):
        """Background thread that reads serial data."""
        while self.running:
            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.queue.put(line)
                        self._parse_line(line)
            except Exception as e:
                print(f"[SERIAL] Read error: {e}")
                time.sleep(0.1)

    def _parse_line(self, line):
        """Parse ESP32 output and update statistics."""
        line_lower = line.lower()

        # Look for beacon detections
        if 'beacon' in line_lower or 'ssid' in line_lower:
            self.stats['beacons_detected'] += 1

        # Look for packet counts
        if 'packet' in line_lower:
            self.stats['packets_captured'] += 1

        # Look for handshake captures
        if 'handshake' in line_lower or 'eapol' in line_lower:
            self.stats['handshakes'] += 1

        # Look for deauth frames
        if 'deauth' in line_lower:
            self.stats['deauths'] += 1

    def get_lines(self, max_lines=None):
        """Get lines from queue (non-blocking)."""
        lines = []
        try:
            while True:
                line = self.queue.get_nowait()
                lines.append(line)
                if max_lines and len(lines) >= max_lines:
                    break
        except queue.Empty:
            pass
        return lines

def find_esp32_port():
    """Auto-detect ESP32 serial port."""
    ports = serial.tools.list_ports.comports()

    # Look for common ESP32 identifiers
    esp32_keywords = ['CP210', 'CH340', 'USB Serial', 'UART', 'ttyUSB', 'ttyACM']

    for port in ports:
        description = port.description.lower()
        device = port.device.lower()

        for keyword in esp32_keywords:
            if keyword.lower() in description or keyword.lower() in device:
                return port.device

    # Fallback: return first available port
    if ports:
        return ports[0].device

    return None

class IntegratedTester:
    """Manages both beacon broadcasting and serial monitoring."""

    def __init__(self, args):
        self.args = args
        self.vif = VirtualInterface()
        self.serial_monitor = None
        self.running = False
        self.broadcast_count = 0
        self.start_time = None

    def setup(self):
        """Setup virtual interface and serial monitor."""
        print("\n" + "="*70)
        print("ESP32 INTEGRATED TESTING TOOL")
        print("="*70 + "\n")

        # Setup serial monitor
        if not self.args.no_serial:
            serial_port = self.args.serial_port
            if not serial_port:
                serial_port = find_esp32_port()
                if serial_port:
                    print(f"[*] Auto-detected ESP32 on: {serial_port}")
                else:
                    print("[!] Could not auto-detect ESP32 port")
                    print("[!] Use --serial-port to specify manually")
                    print("[!] Continuing without serial monitoring...")

            if serial_port:
                self.serial_monitor = SerialMonitor(serial_port, self.args.baudrate)
                if not self.serial_monitor.start():
                    print("[!] Failed to start serial monitor")
                    self.serial_monitor = None

        # Setup virtual interface
        if not self.args.no_virtual:
            base_iface = self.args.interface
            if not base_iface:
                base_iface = self.vif.detect_wireless_interface()
                if base_iface:
                    print(f"[*] Auto-detected wireless interface: {base_iface}")
                else:
                    print("[!] Could not detect wireless interface")
                    return False

            monitor_iface = self.vif.create_virtual_monitor(
                base_iface,
                f'{base_iface}mon'
            )

            if not monitor_iface:
                print("[!] Failed to create virtual monitor interface")
                return False

            self.monitor_interface = monitor_iface
        else:
            self.monitor_interface = self.args.interface

        conf.iface = self.monitor_interface

        return True

    def broadcast_and_monitor(self):
        """Main loop - broadcast beacons and monitor serial."""
        # Prepare beacon frame
        mac = self.args.mac if self.args.mac else generate_random_mac()
        frame = create_beacon_frame(
            self.args.ssid,
            mac,
            self.args.channel,
            not self.args.open
        )

        print("\n" + "="*70)
        print("ACTIVE TESTING SESSION")
        print("="*70)
        print(f"Broadcasting:   SSID: {self.args.ssid} | MAC: {mac} | CH: {self.args.channel}")
        if self.serial_monitor:
            print(f"Monitoring:     {self.serial_monitor.port} @ {self.serial_monitor.baudrate} baud")
        print("="*70 + "\n")

        if self.serial_monitor:
            print("┌─ SERIAL OUTPUT " + "─"*52 + "┐")

        self.running = True
        self.start_time = time.time()
        last_stats_time = time.time()

        try:
            while self.running:
                # Send beacon
                sendp(frame, iface=self.monitor_interface, verbose=False)
                self.broadcast_count += 1

                # Check for serial data
                if self.serial_monitor:
                    lines = self.serial_monitor.get_lines(max_lines=5)
                    for line in lines:
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        # Highlight our test SSID if detected
                        if self.args.ssid in line:
                            print(f"│ [{timestamp}] \033[92m{line}\033[0m")  # Green
                        else:
                            print(f"│ [{timestamp}] {line}")

                # Print stats every 5 seconds
                if time.time() - last_stats_time >= 5:
                    self._print_stats()
                    last_stats_time = time.time()

                time.sleep(self.args.interval)

        except KeyboardInterrupt:
            print("\n\n[!] Stopped by user")

        finally:
            if self.serial_monitor:
                print("└" + "─"*69 + "┘\n")
            self._print_final_stats()

    def _print_stats(self):
        """Print periodic statistics."""
        elapsed = time.time() - self.start_time
        beacon_rate = self.broadcast_count / elapsed if elapsed > 0 else 0

        print("├" + "─"*69 + "┤")
        print(f"│ Stats: Beacons Sent: {self.broadcast_count} | Rate: {beacon_rate:.1f}/s", end="")

        if self.serial_monitor:
            stats = self.serial_monitor.stats
            print(f" | Detected: {stats['beacons_detected']}", end="")

        print(" " * (68 - len(f"Stats: Beacons Sent: {self.broadcast_count} | Rate: {beacon_rate:.1f}/s")) + "│")
        print("├" + "─"*69 + "┤")

    def _print_final_stats(self):
        """Print final statistics."""
        elapsed = time.time() - self.start_time
        beacon_rate = self.broadcast_count / elapsed if elapsed > 0 else 0

        print("\n" + "="*70)
        print("SESSION SUMMARY")
        print("="*70)
        print(f"Runtime:           {elapsed:.1f} seconds")
        print(f"Beacons Sent:      {self.broadcast_count} ({beacon_rate:.1f}/s)")

        if self.serial_monitor:
            stats = self.serial_monitor.stats
            print(f"\nESP32 Detection:")
            print(f"  Beacons Detected: {stats['beacons_detected']}")
            print(f"  Packets Captured: {stats['packets_captured']}")
            print(f"  Handshakes:       {stats['handshakes']}")
            print(f"  Deauths:          {stats['deauths']}")

            if self.broadcast_count > 0 and stats['beacons_detected'] > 0:
                detection_rate = (stats['beacons_detected'] / self.broadcast_count) * 100
                print(f"\nDetection Rate:    {detection_rate:.1f}%")

        print("="*70 + "\n")

    def cleanup(self):
        """Cleanup resources."""
        if self.serial_monitor:
            self.serial_monitor.stop()
        self.vif.cleanup()

def main():
    parser = argparse.ArgumentParser(
        description='Integrated beacon broadcaster + ESP32 serial monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect everything
  sudo python3 integrated_test.py -s "TestAP"

  # Specify serial port
  sudo python3 integrated_test.py -s "TestAP" --serial-port /dev/ttyUSB0

  # Custom MAC and channel
  sudo python3 integrated_test.py -s "MyAP" -m "DE:AD:BE:EF:CA:FE" -c 11

  # Broadcast only (no serial monitoring)
  sudo python3 integrated_test.py -s "TestAP" --no-serial
        """
    )

    # Beacon options
    parser.add_argument('-s', '--ssid', required=True,
                        help='SSID to broadcast')
    parser.add_argument('-m', '--mac', default=None,
                        help='MAC address (random if not specified)')
    parser.add_argument('-c', '--channel', type=int, default=6,
                        help='WiFi channel (1-14, default: 6)')
    parser.add_argument('-t', '--interval', type=float, default=0.1,
                        help='Beacon interval in seconds (default: 0.1)')
    parser.add_argument('--open', action='store_true',
                        help='Broadcast as open network')

    # Interface options
    parser.add_argument('-i', '--interface', default=None,
                        help='Base wireless interface (auto-detect if not specified)')
    parser.add_argument('--no-virtual', action='store_true',
                        help='Skip virtual interface creation')

    # Serial options
    parser.add_argument('--serial-port', default=None,
                        help='ESP32 serial port (auto-detect if not specified)')
    parser.add_argument('--baudrate', type=int, default=115200,
                        help='Serial baudrate (default: 115200)')
    parser.add_argument('--no-serial', action='store_true',
                        help='Skip serial monitoring')

    args = parser.parse_args()

    # Check root
    if os.geteuid() != 0:
        print("[!] ERROR: This script requires root privileges")
        print("[!] Run with: sudo python3 integrated_test.py ...")
        sys.exit(1)

    # Validate inputs
    if len(args.ssid) > 32:
        print("[!] ERROR: SSID must be 32 characters or less")
        sys.exit(1)

    if args.mac and not validate_mac(args.mac):
        print("[!] ERROR: Invalid MAC address format")
        sys.exit(1)

    if not 1 <= args.channel <= 14:
        print("[!] ERROR: Channel must be between 1 and 14")
        sys.exit(1)

    # Run integrated test
    tester = IntegratedTester(args)

    try:
        if not tester.setup():
            print("[!] Setup failed")
            sys.exit(1)

        tester.broadcast_and_monitor()

    finally:
        tester.cleanup()

if __name__ == '__main__':
    main()
