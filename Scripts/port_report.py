#!/usr/bin/env python

#import modules
import csv
import re
import sys
import os
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # get list of IPs to generate port report from
    input_ips = ""
    while input_ips == "":
        input_ips = input('Enter a space delimited list of device IPs: ')

    # gather username and password
    cisco_user = input('Device Username: ')
    cisco_pass = getpass('Device Password: ')
    #sys.stdout.write("Please wait while port report is being generated")
    #sys.stdout.flush()

    with open(os.getcwd()+'/port_report_'+timestamp+'.csv', 'w') as csv_file, open(os.getcwd()+'/port_report_'+timestamp+'.html', 'w') as html_file:

        report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        report_writer.writerow(['Hostname', 'Port', 'Description', 'MAC Address', 'VLAN', 'IP Address'])
        html_file.write("<html>\n<head>\n<title>Cisco Switchport Report</title>\n")
        html_file.write("<style>\n* { padding: 8px; margin: 0; border: 0px; border-spacing: 0px; }\ntr { border-bottom: 1px solid #ccc; }\ntr:first-child { font-weight: bold; }\ntr:nth-child(odd) { background-color: #f2f2f2; }\n</style>\n")
        html_file.write("</head>\n<body>\n<table>\n<tr>\n<td>Hostname</td>\n<td>Interface</td>\n<td>Description</td>\n<td>MAC Address</td>\n<td>VLAN</td>\n<td>IP Address</td>\n</tr>\n")

        for i in input_ips.split():

            conn = {
                "host": i.rstrip('\n'),
                "username": cisco_user,
                "password": cisco_pass,
                "device_type": "cisco_ios",
            }

            try:
                net_connect = Netmiko(**conn)
                vers = net_connect.send_command('show version')
            except:
                #sys.stdout.write("!")
                #sys.stdout.flush()
                print(f'Error Connecting to {i}') 
            else:
                hostname = net_connect.find_prompt().split('#')[0]
                if "Nexus" in vers:
                    int_list = net_connect.send_command('show interface brief')
                else:
                    int_list = net_connect.send_command('show ip interface brief')
                for j in int_list.splitlines():
                    if "down" not in j and "up" in j:
                        int_conf = net_connect.send_command("show run int "+j.split()[0])
                        if "mode trunk" not in int_conf:
                            desc = "none"
                            mac_add = "not found"
                            vlan_id = "none"
                            vendor = "not found"
                            ip_add = "not found"
                            for k in int_conf.splitlines():
                                if "description" in k:
                                    desc = k[13:]
                            mac_list = net_connect.send_command("show mac address interface "+j.split()[0])
                            for l in mac_list.splitlines():
                                if re.search('([0-9a-fA-F]\.?){12}', l):
                                    if l.split()[0] == "*":
                                        vlan_id = l.split()[1]
                                        mac_add = l.split()[2]
                                    else:
                                        vlan_id = l.split()[0]
                                        mac_add = l.split()[1]
                                    ip_list = net_connect.send_command("show ip arp | inc "+mac_add)
                                    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_list):
                                        ip_add = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_list).group(1)
                                    report_writer.writerow([hostname, j.split()[0], desc, mac_add, vlan_id, ip_add])
                                    html_file.write("<tr>\n<td>"+hostname+"</td>\n<td>"+j.split()[0]+"</td>\n<td>"+desc+"</td>\n<td>"+mac_add+"</td>\n<td>"+vlan_id+"</td>\n<td>"+ip_add+"</td>\n</tr>\n")
                net_connect.disconnect()
                #sys.stdout.write(".")
                #sys.stdout.flush()
        html_file.write("</table>\n</body>\n</html>")
    print('Port report has been generated')

    main()
