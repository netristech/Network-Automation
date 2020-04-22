#!/usr/bin/env python

#import modules
import csv
#import re
import sys
import os
import ipaddress
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # gather list of device IPs used to generate VLAN list
    while True:
        try:
            dev_ips = input("Enter a space delimited list of device IPs: ").split()
            for i in range(0, len(dev_ips)):
                dev_ips[i] = ipaddress.IPv4Address(dev_ips[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break
    
    if len(dev_ips) > 0:
        
        # gather username and password
        cisco_user = input("Device Username: ")
        cisco_pass = getpass("Device Password: ")

        for ip in dev_ips:
            
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
                print(f"Could not connect to device at {str(ip)}")
            else:
                hostname = net_connect.find_prompt().split('#')[0]
                stack = net_connect.send_command("show switch")
                for switch in stack.splitlines():
                    if len(switch) > 0:
                        if switch.split()[0].startswith("*"):
                            switch = switch.lstrip("*")
                        if switch.split()[0].isdigit():
                            print(switch)
                vers_list = net_connect.send_command("show version | begin [\*]").splitlines()[0:len(switch)]
                for line in vers_list:
                    if len(line) > 0:
                        print(line)
                net_connect.disconnect()
main()
print("\nVlan report has been generated")
