#!/usr/bin/env python

#import modules
import re
import sys
import os
import ipaddress
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

def main():

    # generate input_file from input_subnets containing all IPs to perform inventory scan against
    while True:
        try:
            input_ips = input("Enter a space delimited list of IPs to scan: ").split()
            for i in range(0, len(input_ips)):
                input_ips[i] = ipaddress.IPv4Address(input_ips[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break
    
    if len(input_ips) > 0:

        # gather username and password
        cisco_user = input("Device Username: ")
        cisco_pass = getpass("Device Password: ")
        sys.stdout.write("Please wait while inventory report is being generated")
        sys.stdout.flush()

        for ip in input_ips:
                # Create connection object for Netmiko
                conn = {
                    "host": str(ip),
                    "username": cisco_user,
                    "password": cisco_pass,
                    "device_type": "cisco_ios",
                }

                # Attempt connection
                try:
                    net_connect = Netmiko(**conn)
                    vers = net_connect.send_command('show version')
                except:
                    print(f"Error connecting to {str(ip)}")
                else:
                    
                    # Special handling for Nexus
                    if "Nexus" in vers:
                        ports = net_connect.send_command('show int bri | inc "Administratively"')
                    # Normal handling for IOS
                    else:
                        ports = net_connect.send_command('show ip int bri | inc administratively')
                    for line in ports.splitlines():
                        int = line.split()[0]
                        if int.startswith('Gig'):
                            net_connect.send_config_set([f'interface {int}', f'no shutdown'])
                    net_connect.save_config()
                    net_connect.disconnect()

main()
print("\nAll ports have been brought up.")