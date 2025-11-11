#!/usr/bin/env python3
"""
WiFi Beacon Broadcaster with Virtual NIC Support
Automatically creates a virtual monitor interface without disrupting your existing WiFi.

Author: ESP32 War Driving Project
License: Educational/Testing Use Only
"""

import argparse
import sys
import time
import random
import subprocess
import os
import re
from scapy.all import (
    RadioTap, Dot11, Dot11Beacon, Dot11Elt,
    sendp, conf, get_if_list
)

class VirtualInterface:
    """Manages virtual wireless interfaces for beacon broadcasting."""

    def __init__(self, base_interface=None):
        self.base_interface = base_interface
        self.virtual_interface = None
        self.created = False

    def detect_wireless_interface(self):
        """Auto-detect a wireless interface."""
        try:
            result = subprocess.run(
                ['iw', 'dev'],
                capture_output=True,
                text=True,
                check=False
            )

            # Parse iw dev output for Interface names
            matches = re.findall(r'Interface\s+(\w+)', result.stdout)

            for iface in matches:
                if iface.startswith('wl'):
                    return iface

            # Fallback: check common names
            common_names = ['wlan0', 'wlp2s0', 'wlp3s0', 'wlo1']
            available = get_if_list()
            for name in common_names:
                if name in available:
                    return name

        except Exception as e:
            print(f"[!] Error detecting interface: {e}")

        return None

    def check_monitor_support(self, interface):
        """Check if interface supports monitor mode."""
        try:
            result = subprocess.run(
                ['iw', 'phy'],
                capture_output=True,
                text=True,
                check=False
            )

            # Look for monitor mode support
            return 'monitor' in result.stdout.lower()

        except Exception:
            return False

    def create_virtual_monitor(self, base_iface, virtual_name='wlan0mon'):
        """Create a virtual monitor interface."""
        try:
            print(f"[*] Creating virtual monitor interface: {virtual_name}")
            print(f"[*] Base interface: {base_iface}")

            # Check if virtual interface already exists
            if virtual_name in get_if_list():
                print(f"[!] Interface {virtual_name} already exists, using it...")
                self.virtual_interface = virtual_name
                self.created = False  # Didn't create it, so don't destroy it
                return virtual_name

            # Create virtual interface
            result = subprocess.run(
                ['iw', 'dev', base_iface, 'interface', 'add', virtual_name, 'type', 'monitor'],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                print(f"[!] Failed to create virtual interface: {result.stderr}")
                return None

            # Bring interface up
            subprocess.run(['ip', 'link', 'set', virtual_name, 'up'], check=False)

            # Verify it was created
            if virtual_name not in get_if_list():
                print(f"[!] Virtual interface creation failed")
                return None

            print(f"[+] Virtual interface {virtual_name} created successfully!")
            print(f"[+] Your main WiFi on {base_iface} should still work!")

            self.virtual_interface = virtual_name
            self.created = True
            return virtual_name

        except Exception as e:
            print(f"[!] Exception creating virtual interface: {e}")
            return None

    def cleanup(self):
        """Remove virtual interface if we created it."""
        if self.created and self.virtual_interface:
            try:
                print(f"\n[*] Cleaning up virtual interface: {self.virtual_interface}")
                subprocess.run(
                    ['iw', 'dev', self.virtual_interface, 'del'],
                    capture_output=True,
                    check=False
                )
                print(f"[+] Virtual interface removed")
            except Exception as e:
                print(f"[!] Error during cleanup: {e}")

def validate_mac(mac):
    """Validate MAC address format."""
    parts = mac.split(':')
    if len(parts) != 6:
        return False
    try:
        return all(0 <= int(part, 16) <= 255 for part in parts)
    except ValueError:
        return False

def generate_random_mac():
    """Generate a random MAC address."""
    # First byte should be even for unicast, and locally administered
    first = random.randint(0, 255) & 0xFE | 0x02
    rest = [random.randint(0, 255) for _ in range(5)]
    return '%02x:%s' % (first, ':'.join('%02x' % b for b in rest))

def create_beacon_frame(ssid, bssid, channel=1, encrypted=True):
    """
    Create a WiFi beacon frame.

    Args:
        ssid: Network name to broadcast
        bssid: MAC address of the fake AP
        channel: WiFi channel (1-14)
        encrypted: Show as encrypted network

    Returns:
        Scapy packet ready to send
    """
    # 802.11 Management frame
    dot11 = Dot11(
        type=0,           # Management frame
        subtype=8,        # Beacon subtype
        addr1='ff:ff:ff:ff:ff:ff',  # Destination (broadcast)
        addr2=bssid,      # Source (our fake AP)
        addr3=bssid       # BSSID (our fake AP)
    )

    # Beacon frame with capabilities
    cap = 'ESS'
    if encrypted:
        cap += '+privacy'

    beacon = Dot11Beacon(
        cap=cap,
        timestamp=int(time.time() * 1000000)  # Microseconds
    )

    # Information elements
    essid = Dot11Elt(ID='SSID', info=ssid.encode(), len=len(ssid))

    # Supported rates (802.11b/g/n compatible)
    rates = Dot11Elt(ID='Rates', info=b'\x82\x84\x8b\x96\x24\x30\x48\x6c')

    # DS Parameter set (channel)
    dsset = Dot11Elt(ID='DSset', info=bytes([channel]))

    # Traffic Indication Map
    tim = Dot11Elt(ID='TIM', info=b'\x00\x01\x00\x00')

    # Extended supported rates
    ext_rates = Dot11Elt(ID='ESRates', info=b'\x0c\x12\x18\x60')

    # Assemble the complete frame
    frame = RadioTap() / dot11 / beacon / essid / rates / dsset / tim / ext_rates

    return frame

def broadcast_beacon(interface, ssid, mac, channel=6, interval=0.1, count=None,
                     encrypted=True, verbose=True):
    """
    Broadcast beacon frames continuously.

    Args:
        interface: Network interface to use (must be in monitor mode)
        ssid: SSID to broadcast
        mac: MAC address to use
        channel: WiFi channel (1-14)
        interval: Time between beacons in seconds
        count: Number of beacons to send (None = infinite)
        encrypted: Show as encrypted network
        verbose: Print status messages
    """
    # Set scapy to use the specified interface
    conf.iface = interface

    # Create the beacon frame
    frame = create_beacon_frame(ssid, mac, channel, encrypted)

    if verbose:
        print(f"\n{'='*60}")
        print(f"[+] BEACON BROADCASTER ACTIVE")
        print(f"{'='*60}")
        print(f"[+] Interface: {interface}")
        print(f"[+] SSID: {ssid}")
        print(f"[+] MAC: {mac}")
        print(f"[+] Channel: {channel}")
        print(f"[+] Security: {'WPA/WPA2' if encrypted else 'Open'}")
        print(f"[+] Interval: {interval}s")
        print(f"[+] Press Ctrl+C to stop")
        print(f"{'='*60}\n")

    sent = 0
    start_time = time.time()

    try:
        while count is None or sent < count:
            sendp(frame, iface=interface, verbose=False)
            sent += 1

            if verbose and sent % 10 == 0:
                elapsed = time.time() - start_time
                rate = sent / elapsed if elapsed > 0 else 0
                print(f"\r[*] Beacons sent: {sent} | Rate: {rate:.1f}/s", end='', flush=True)

            time.sleep(interval)

    except KeyboardInterrupt:
        if verbose:
            elapsed = time.time() - start_time
            print(f"\n\n[!] Stopped by user")
            print(f"[+] Total beacons sent: {sent}")
            print(f"[+] Runtime: {elapsed:.1f}s")
            print(f"[+] Average rate: {sent/elapsed:.1f} beacons/s")
    except PermissionError:
        print("\n[!] ERROR: Need root privileges. Run with sudo.")
        sys.exit(1)
    except OSError as e:
        print(f"\n[!] ERROR: {e}")
        print(f"[!] Make sure interface '{interface}' exists and is in monitor mode")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Broadcast WiFi beacons with automatic virtual interface creation',
        epilog='Example: sudo python3 beacon_broadcast.py -s "FreeWiFi" -m "DE:AD:BE:EF:CA:FE"',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-i', '--interface', default=None,
                        help='Base wireless interface (auto-detect if not specified)')

    parser.add_argument('-s', '--ssid', required=True,
                        help='SSID to broadcast (max 32 characters)')

    parser.add_argument('-m', '--mac', default=None,
                        help='MAC address (e.g., AA:BB:CC:DD:EE:FF). Random if not specified.')

    parser.add_argument('-c', '--channel', type=int, default=6,
                        help='WiFi channel (1-14, default: 6)')

    parser.add_argument('-t', '--interval', type=float, default=0.1,
                        help='Time between beacons in seconds (default: 0.1)')

    parser.add_argument('-n', '--count', type=int, default=None,
                        help='Number of beacons to send (default: infinite)')

    parser.add_argument('--open', action='store_true',
                        help='Broadcast as open network (default: shows as encrypted)')

    parser.add_argument('--no-virtual', action='store_true',
                        help='Skip virtual interface creation (use existing monitor interface)')

    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Quiet mode (minimal output)')

    args = parser.parse_args()

    # Check root
    if os.geteuid() != 0:
        print("[!] ERROR: This script requires root privileges")
        print("[!] Run with: sudo python3 beacon_broadcast.py ...")
        sys.exit(1)

    # Validate SSID length
    if len(args.ssid) > 32:
        print("[!] ERROR: SSID must be 32 characters or less")
        sys.exit(1)

    # Validate or generate MAC address
    if args.mac:
        if not validate_mac(args.mac):
            print("[!] ERROR: Invalid MAC address format")
            print("[!] Expected format: AA:BB:CC:DD:EE:FF")
            sys.exit(1)
        mac = args.mac
    else:
        mac = generate_random_mac()
        if not args.quiet:
            print(f"[*] Generated random MAC: {mac}")

    # Validate channel
    if not 1 <= args.channel <= 14:
        print("[!] ERROR: Channel must be between 1 and 14")
        sys.exit(1)

    # Virtual interface management
    vif = VirtualInterface()
    monitor_interface = None

    try:
        if args.no_virtual:
            # Use existing monitor interface
            monitor_interface = args.interface
            if not monitor_interface:
                print("[!] ERROR: --no-virtual requires -i <interface>")
                sys.exit(1)
        else:
            # Detect base interface
            base_iface = args.interface
            if not base_iface:
                base_iface = vif.detect_wireless_interface()
                if not base_iface:
                    print("[!] ERROR: Could not detect wireless interface")
                    print("[!] Please specify with -i <interface>")
                    sys.exit(1)
                if not args.quiet:
                    print(f"[*] Detected wireless interface: {base_iface}")

            # Check monitor support
            if not vif.check_monitor_support(base_iface):
                print("[!] WARNING: Monitor mode support unclear")
                print("[!] Attempting to create virtual interface anyway...")

            # Create virtual monitor interface
            monitor_interface = vif.create_virtual_monitor(
                base_iface,
                f'{base_iface}mon'
            )

            if not monitor_interface:
                print("[!] ERROR: Failed to create virtual monitor interface")
                print("[!] Your wireless card may not support virtual interfaces")
                print("[!] Try running with --no-virtual and manually create monitor interface")
                sys.exit(1)

        # Start broadcasting
        broadcast_beacon(
            interface=monitor_interface,
            ssid=args.ssid,
            mac=mac,
            channel=args.channel,
            interval=args.interval,
            count=args.count,
            encrypted=not args.open,
            verbose=not args.quiet
        )

    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Cleanup virtual interface
        vif.cleanup()

if __name__ == '__main__':
    main()
