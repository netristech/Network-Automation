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
                print(hostname)
                stack = net_connect.send_command("show switch")
                if len(stack) > 0:
                    for switch in stack.splitlines():
                        if len(switch) > 0:
                            if switch.split()[0].startswith("*"):
                                switch = switch.lstrip("*")
                            if switch.split()[0].isdigit():
                                print(switch)
                '''
                switch_vers = vers[slice(vers.find("* "), vers.find(""), 1)]
                if len(switch_vers) > 0:
                    switch_vers = switch_vers.splitlines()
                    while "" in switch_vers:
                        switch_vers.remove("")
                if len(switch_vers) > 0:
                    for line in switch_vers:
                        print(line)
                '''        
                switch_vers = []
                switch_SNs = []
                for line in vers.splitlines():
                    if line.startswith("System Serial Number"):
                        switch_SNs.append(line.split()[4])
                    if "INSTALL" in line:
                        if line.startswith("*"):
                            line = line.lstrip("*")
                        switch_vers.append(line)
                if len(switch_vers) > 0:
                    for line in switch_vers:
                        print(line)
                if len(switch_SNs) > 0:
                    for line in switch_SNs:
                        print(line)
                mgmt_ips = net_connect.send_command("show running-config interface Vlan 1")
                mgmt_ip = "unknown"
                if len(mgmt_ips) > 0:
                    for ip in mgmt_ips.splitlines():
                        if ip.lstrip().startswith("ip address"):
                            mgmt_ip = f"{ip.split()[2]} {ip.split()[3]}"
                print(mgmt_ip)
                def_route = net_connect.send_command("show running-config | inc ip default").split()[2]
                print(def_route)
                net_connect.disconnect()
main()
