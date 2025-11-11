#!/usr/bin/env python3
"""
Beacon Flood Tester - Sends beacons with different MACs each time
This ensures ESP32 prints [NEW DEVICE] for every beacon
"""

import sys
import time
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from beacon_broadcast import (
    generate_random_mac,
    create_beacon_frame,
    VirtualInterface
)
from scapy.all import sendp, conf

def flood_test(interface, ssid, channel=6, count=20, interval=1.0):
    """Send beacons with different MACs to trigger ESP32 detection."""

    conf.iface = interface

    print(f"[*] Sending {count} beacons on channel {channel}")
    print(f"[*] SSID: {ssid}")
    print(f"[*] Each beacon uses a DIFFERENT MAC (to trigger ESP32)")
    print(f"[*] Interval: {interval}s between beacons")
    print()

    for i in range(count):
        # Generate new MAC for each beacon
        mac = generate_random_mac()
        frame = create_beacon_frame(ssid, mac, channel, encrypted=True)

        sendp(frame, iface=interface, verbose=False)

        print(f"[{i+1}/{count}] Sent beacon from MAC: {mac}")

        time.sleep(interval)

    print()
    print(f"[+] Sent {count} beacons with unique MACs")
    print(f"[+] ESP32 should have detected multiple [NEW DEVICE] entries")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Send beacons with different MACs')
    parser.add_argument('-i', '--interface', required=True, help='Monitor interface')
    parser.add_argument('-s', '--ssid', required=True, help='SSID to broadcast')
    parser.add_argument('-c', '--channel', type=int, default=6, help='Channel (default: 6)')
    parser.add_argument('-n', '--count', type=int, default=20, help='Number of beacons (default: 20)')
    parser.add_argument('-t', '--interval', type=float, default=1.0, help='Interval in seconds (default: 1.0)')

    args = parser.parse_args()

    if os.geteuid() != 0:
        print("[!] Must run as root: sudo python3 flood_test.py ...")
        sys.exit(1)

    flood_test(args.interface, args.ssid, args.channel, args.count, args.interval)
