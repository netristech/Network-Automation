#!/usr/bin/env python

#imports
#from __future__ import print_function
import sys
import os
import re
import ipaddress
#import csv
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

def main():
    while True:
        try:
            dev_ips = input("Destination IP or IPs (space delimited): ").split()
            for i in range(0, len(dev_ips)):
                dev_ips[i] = ipaddress.IPv4Address(dev_ips[i])
            add_ips = input("DHCP relay IP(s) to add (space delimited): ").split()
            for i in range(0, len(add_ips)):
                add_ips[i] = ipaddress.IPv4Address(add_ips[i])
            rem_ips = input("DHCP relay IP(s) to remove (space delimited): ").split()
            for i in range(0, len(rem_ips)):
                rem_ips[i] = ipaddress.IPv4Address(rem_ips[i])                
            vlans = input("VLAN ID(s) to update (number only, space delimited): ").split()
            for i in range(0, len(vlans)):
                if not vlans[i].isnumeric() or int(vlans[i]) < 0 or int(vlans[i]) > 4094:
                    vlans.pop(i)
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break

    if len(add_ips) > 0 or len(rem_ips) > 0:
        # gather username and password
        cisco_user = input("username: ")
        cisco_pass = getpass()
        add_comm = "ip helper-address "
        rem_comm = "no ip helper-address "
        print("Please wait while the update is being performed")
        
        for ip in dev_ips:
            conn = {
                "host": str(ip).rstrip("\n"),
                "username": cisco_user,
                "password": cisco_pass,
                "device_type": "cisco_ios",
            }

            try:
                net_connect = Netmiko(**conn)
                vers = net_connect.send_command('show version')
            except:
                print(f"Connection to {ip} failed")
            else:
                hostname = net_connect.find_prompt().split('#')[0]
                # Special handling for Nexus
                if "Nexus" in vers:
                    add_comm = "ip dhcp relay address "
                    rem_comm = "no ip dhcp relay address "
                for vlan in vlans:
                    for i in rem_ips:
                        net_connect.send_config_set(['interface vlan '+vlan, rem_comm+str(i)])
                    for i in add_ips:
                        net_connect.send_config_set(['interface vlan '+vlan, add_comm+str(i)])
                    print(f"Updated DHCP relays for VLAN {vlan}")
                net_connect.disconnect()
                print(f"Successfully updated DHCP relays on {hostname}")
main()
print("\nUpdate completed!")
