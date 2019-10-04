#!/usr/bin/env python

#import modules
import csv
import re
import sys
import os
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# generate input_file from input_subnets containing all IPs to perform inventory scan against
input_subnets = ""
while input_subnets == "":
    input_subnets = raw_input("Enter a space delimited list of subnets (in CIDR notation) to scan: ")
input_file = os.getcwd()+"/ips_"+timestamp
input_subnets = input_subnets.split(" ")
for i in input_subnets:
    os.system("sudo "+os.getcwd()+"/discover_devices.sh "+i+" "+input_file)
print "Generating IP list. This may take a moment. . ."

# gather username and password
cisco_user = raw_input("Login username: ")
cisco_pass = getpass()
sys.stdout.write("Please wait while inventory report is being generated")
sys.stdout.flush()

with open(os.getcwd()+'/inventory_'+timestamp+'.csv', 'w') as csv_file, open(input_file) as file:

    report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    report_writer.writerow(['Hostname', 'IP Address', 'Model', 'Software Version', 'Serial Number'])

    for line in file:

        conn = {
            "host": line.rstrip("\n"),
            "username": cisco_user,
            "password": cisco_pass,
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
            # Special handling for Nexus
            if "Nexus" in vers:
                inv = net_connect.send_command('show inventory')
                version = vers[vers.find("system:    version ") + 19:].splitlines()[0].strip()
                model = vers[vers.find("cisco Nexus ") + 6:vers.find("Chassis (") - 1]
                serials.append(inv[inv.find("SN: ") + 4:].splitlines()[0].strip())
            # Normal handling for IOS
            else:
                version = vers[vers.find("), Version") + 11:vers.find("RELEASE") - 2]
                model_ind = vers[:vers.find(") processor")].splitlines()
                model = model_ind[len(model_ind) - 1].split(" ")[1]
                for i in re.finditer('System Serial Number', vers, re.IGNORECASE):
                    serials.append(vers[i.start():].splitlines()[0].split(":")[1].strip())
            report_writer.writerow([hostname, line.rstrip("\n"), model, version, serials[0]])
            if len(serials) > 1:
                for x in range(1, len(serials)):
                    report_writer.writerow([hostname+'-{}'.format(x + 1), '(stacked)', model, '(stacked)', serials[x]])
            net_connect.disconnect()
            sys.stdout.write(".")
            sys.stdout.flush()
print "\nInventory report has been generated"