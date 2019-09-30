#! /usr/bin/env python
import csv
import re
import sys
import os
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

input_file = raw_input("Name of file containing IP list [default 'ips']: ")
if input_file == "":
    input_file = "ips"
ciscouser = raw_input("Login username: ")
ciscopass = getpass()
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
sys.stdout.write("Please wait while inventory report is being generated")
sys.stdout.flush()

with open(os.getcwd()+'/inventory_'+datetime.now().strftime('%Y%m%d%H%M%S')+'.csv', 'w') as csv_file, open(os.getcwd()+'/'+input_file) as file:

    report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    report_writer.writerow(['Hostname', 'IP Address', 'Software Version', 'Serial Number'])

    for line in file:

        conn = {
            "host": line.rstrip("\n"),
            "username": ciscouser,
            "password": ciscopass,
            "device_type": "cisco_ios",
        }

        try:
            net_connect = Netmiko(**conn)
        except:
            sys.stdout.write("!")
            sys.stdout.flush()
        else:
            serials = []
            hostname = net_connect.find_prompt().split('#')[0]
            vers = net_connect.send_command('show version')
            # Special handling for Nexus switches
            if "Nexus" in vers:
                inv = net_connect.send_command('show inventory')
                version = vers[vers.find("system:    version ") + 19:].splitlines()[0].strip()
                serials.append(inv[inv.find("SN: ") + 4:].splitlines()[0].strip())
            # Normal handling for IOS switches
            else:
                version = vers[vers.find("), Version") + 11:vers.find("RELEASE") - 2]
                for i in re.finditer('System Serial Number', vers, re.IGNORECASE):
                    serials.append(vers[i.start():].splitlines()[0].split(":")[1].strip())
            report_writer.writerow([hostname, line.rstrip("\n"), version, serials[0]])
            if len(serials) > 1:
                for x in range(1, len(serials)):
                    report_writer.writerow([hostname+'-SW{}'.format(x), '(stacked)', '(stacked)', serials[x]])
            net_connect.disconnect()
            sys.stdout.write(".")
            sys.stdout.flush()
print "\nInventory report has been generated"