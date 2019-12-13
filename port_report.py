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

# get list of IPs to generate port report from
input_ips = ""
while input_ips == "":
    input_ips = raw_input("Enter a space delimited list of the switch IP addresses: ")

# gather username and password
cisco_user = raw_input("Username: ")
cisco_pass = getpass()
sys.stdout.write("Please wait while port report is being generated")
sys.stdout.flush()

with open(os.getcwd()+'/port_report('+timestamp+').csv', 'w') as csv_file, 
    open(os.getcwd()+'/port_report('+timestamp+').html', 'w') as html_file:

    report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    report_writer.writerow(['Hostname', 'Port', 'Description', 'MAC Address', 'VLAN', 'IP Address'])
    html_file.write("<html>\n<head>\n<title>Cisco Switchport Report</title>\n")
    html_file.write("<style>\n* { padding: 8px; }\n</style>\n</head>\n<body>\n<table>\n")
    html_file.write("<tr>\n<td>Hostname</td>\n<td>Interface</td>\n<td>Description</td>\n<td>MAC Address</td>\n<td>VLAN</td>\n<td>IP Address</td>\n</tr>\n")

    for i in input_ips.split():

        conn = {
            "host": i.rstrip("\n"),
            "username": cisco_user,
            "password": cisco_pass,
            "device_type": "cisco_ios",
        }

        try:
            net_connect = Netmiko(**conn)
            vers = net_connect.send_command('show version')
        except:
            sys.stdout.write("!")
            sys.stdout.flush()
        else:
            hostname = net_connect.find_prompt().split('#')[0]
            if "Nexus" in vers:
                int_list = net_connect.send_command("show interface brief")
            else:
                int_list = net_connect.send_command("show ip interface brief")
            for j in int_list.splitlines():
                if "down" not in j:
                    int_conf = net_connect.send_command("show run int "+j.split()[0])
                    if "mode trunk" not in int_conf:
                        desc = "none"
                        mac_add = "not found"
                        ip_add = "not found"
                        for k in int_conf.splitlines():
                            if "description" in k:
                            desc = k
                        mac_list = net_connect.send_command("show mac add int "+j.split()[0])
                        for l in mac_list.splitlines():
                            if re.search('([0-9A-F]{4}[\.-]){2}[0-9A-F]{4}', l):
                                if l.split()[0] == "*":
                                    vlan_id = l.split()[1]
                                    mac_add = l.split()[2]
                                else:
                                    vlan_id = l.split()[0]
                                    mac_add = l.split()[1]
                                ip_list = net_connect.send_command("sh ip arp | inc "+mac_add)
                                if re.search('([0-9]{1,3}[\.-]){3}[0-9]{1,3}', ip_list):
                                    ip_add = re.search('([0-9]{1,3}[\.-]){3}[0-9]{1,3}', ip_list).group(1).strip()
                            report_writer.writerow([hostname, j.split()[0], desc, mac_add, vlan_id, ip_add])
                            html_file.write("<tr>\n<td>"+hostname+"</td>\n<td>"+j.split()[0]+"</td>\n<td>"+desc+"</td>\n<td>"+mac_add+"</td>\n<td>"+vlan_id+"</td>\n<td>"+ip_add+"</td>\n</tr>\n")
            net_connect.disconnect()
            sys.stdout.write(".")
            sys.stdout.flush()
    html_file.write("</table>\n</body>\n</html>")
print "\nInventory report has been generated"