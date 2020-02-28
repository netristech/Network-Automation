#!/usr/bin/env python

#import modules
import csv
import re
import sys
import os
import ipaddress
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # generate input_file from input_subnets containing all IPs to perform inventory scan against
    while True:
        try:
            input_subnets = input("Enter a space delimited list of subnets (in CIDR notation) to scan: ").split()
            for i in range(0, len(input_subnets)):
                input_subnets[i] = ipaddress.IPv4Network(input_subnets[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break
    
    if len(input_subnets) > 0:

        # Generate IP file
        input_file = f"{os.getcwd()}/ips_{timestamp}"
        for i in input_subnets:
            os.system(f"sudo {os.getcwd()}/discover_devices.sh {i} {input_file}")        
        
        # gather username and password
        cisco_user = input("Device Username: ")
        cisco_pass = getpass("Device Password: ")
        sys.stdout.write("Please wait while inventory report is being generated")
        sys.stdout.flush()
        
        # Open csv file for write operation
        with open(f'{os.getcwd()}/inv_{timestamp}.csv', 'w') as csv_file, open(input_file) as file:
            report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            report_writer.writerow(['Hostname', 'IP Address', 'Model', 'Software Version', 'Serial Number'])
            for line in file:
                
                # Create connection object for Netmiko
                conn = {
                    "host": line.rstrip("\n"),
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
                    serials = []
                    hostname = net_connect.find_prompt().split('#')[0]
                    
                    # Special handling for Nexus
                    if "Nexus" in vers:
                        inv = net_connect.send_command('show inventory')
                        version = vers[vers.find("system:    version ") + 19:].splitlines()[0].strip()
                        #model = vers[vers.find("cisco Nexus ") + 6:vers.find("Chassis (") - 1]
                        model = inv[inv.find("PID: ") + 5:].splitlines()[0].strip()
                        serials.append(inv[inv.find("SN: ") + 4:].splitlines()[0].strip())
                    
                    # Normal handling for IOS
                    else:
                        version = vers[vers.find("), Version") + 11:vers.find("RELEASE") - 2]
                        model = re.search("cisco(.+?)processor", vers).group(1).split()[0]
                        for i in re.finditer('System Serial Number', vers, re.IGNORECASE):
                            serials.append(vers[i.start():].splitlines()[0].split(":")[1].strip())
                    report_writer.writerow([hostname, line.rstrip("\n"), model, version, serials[0]])
                    if len(serials) > 1:
                        for x in range(1, len(serials)):
                            report_writer.writerow([hostname+'-{}'.format(x + 1), '(stacked)', '(stacked)', '(stacked)', serials[x]])
                    net_connect.disconnect()
                    sys.stdout.write(".")
                    sys.stdout.flush()
main()
print("\nInventory report has been generated")