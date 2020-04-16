#!/usr/bin/env python

#import modules
import csv
#import re
import sys
import os
import ipaddress
#from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

def main():
    #timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

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
        sys.stdout.write("Please wait while inventory report is being generated")
        sys.stdout.flush()
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
                sys.stdout.write("!")
                sys.stdout.flush()
            else:
                hostname = net_connect.find_prompt().split('#')[0]
                with open(f'{os.getcwd()}/{hostname}_vlans.csv', 'w') as csv_file:
                    report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    report_writer.writerow(['VLAN ID', 'VLAN Description', 'Subnet'])
                    vlans = net_connect.send_command("show vlan brief")
                    for vlan in vlans.splitlines():
                        if vlan.split()[0].isdigit() == True:
                            vlan_id = vlan.split()[0]
                            vlan_desc = vlan.split()[1]
                            svi = net_connect.send_command(f"show run interface Vlan{vlan_id}")
                            for line in svi.splitlines():
                                if line.startswith("ip address "):
                                    subnet = ipaddress.IPv4Network(line.split()[2:])
                            report_writer.writerow([vlan_id, vlan_desc, str(subnet)])
                net_connect.disconnect()
                sys.stdout.write(".")
                sys.stdout.flush()
main()
print("\nVlan report has been generated")
