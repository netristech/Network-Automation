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
        sys.stdout.write("Please wait while inventory report is being generated")
        sys.stdout.flush()

        # Open CSV file for writing
        with open(f"{os.getcwd()}/switch_report_{timestamp}.csv", "w") as csv_file:
            report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)      
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
                    # Setup initial values
                    vars = []
                    sw_role = ['Role']
                    sw_mac = ['MAC Address']
                    sw_prio = ['Priority']
                    sw_hwver = ['H/W Version']
                    sw_ports = ['Number of Ports']
                    sw_model = ['Model']
                    sw_swver = ['S/W Version']
                    sw_image = ['S/W Image']
                    sw_sn = ['Serial Number']
                    hostname = net_connect.find_prompt().split('#')[0]
                    def_route = "unknown"

                    # Setup Heading in Report
                    report_writer.writerow([hostname, '', ''])
                    report_writer.writerow(['','',''])
                    report_writer.writerow(['Item', '', 'Specification'])                    

                    # Collect data
                    stack = net_connect.send_command("show switch")                    
                    if len(stack) > 0:
                        for switch in stack.splitlines():
                            if len(switch) > 0:
                                if switch.split()[0].startswith("*"):
                                    switch = switch.lstrip("*")
                                if switch.split()[0].isdigit():
                                    sw_role.append(switch.split()[1])
                                    sw_mac.append(switch.split()[2])
                                    sw_prio.append(switch.split()[3])
                                    sw_hwver.append(switch.split()[4])
                    for line in vers.splitlines():
                        if line.startswith("System Serial Number"):
                            sw_sn.append(line.split()[4])
                        if "INSTALL" in line:
                            if line.startswith("*"):
                                line = line.lstrip("*")
                            sw_ports.append(line.split()[1])
                            sw_model.append(line.split()[2])
                            sw_swver.append(line.split()[3])
                            sw_image.append(line.split()[4])
                    mgmt_ips = net_connect.send_command("show running-config interface Vlan 1")
                    mgmt_ip = "unknown"
                    if len(mgmt_ips) > 0:
                        for ip in mgmt_ips.splitlines():
                            if ip.lstrip().startswith("ip address"):
                                mgmt_ip = f"{ip.split()[2]} {ip.split()[3]}"
                    try:
                        def_route = net_connect.send_command("show running-config | inc ip default").split()[2]
                    except:
                        try:
                            def_route = net_connect.send_command("show running-config | inc ip route 0.0.0.0").split()[4]
                        except:
                            pass

                    # Build report
                    vars = [sw_role, sw_mac, sw_prio, sw_hwver, sw_ports, sw_model, sw_swver, sw_image, sw_sn]
                    for i in range(0, len(vars), 1):
                        if len(vars[i]) > 1:
                            report_writer.writerow([vars[i][0], f"Switch# {i + 1}", vars[i][1]])
                        if len(vars[i]) > 2:
                            for j in range(2, len(vars[i]), 1):
                                report_writer.writerow(['', f'Switch# {j}', vars[i][j]])
                    report_writer.writerow(['Management Information', 'Hostname', hostname])
                    report_writer.writerow(['', 'IP Address', mgmt_ip])
                    report_writer.writerow(['', 'Gateway', def_route])
                    net_connect.disconnect()
                    sys.stdout.write(".")
                    sys.stdout.flush()
main()
print("\nSwitch report has been generated")
