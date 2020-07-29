#!/usr/bin/env python

#import modules
import csv
import os
import re
import ipaddress
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko

def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # get list of IPs to generate port report from
    while True:
        try:
            input_ips = input("Enter a space delimited list of device IPs: ").split()
            for i in range(0, len(input_ips)):
                input_ips[i] = ipaddress.ip_address(input_ips[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break

    if len(input_ips) > 0:                

        # gather username and password
        cisco_user = input('Device Username: ')
        cisco_pass = getpass('Device Password: ')
        print("Please wait while port report is being generated")

        with open(os.getcwd()+'/port_report_'+timestamp+'.csv', 'w') as csv_file, open(os.getcwd()+'/port_report_'+timestamp+'.html', 'w') as html_file:

            report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            report_writer.writerow(['Hostname', 'Interface', 'Status', 'Description', 'MAC Address', 'VLAN', 'IP Address'])
            html_file.write("<html>\n<head>\n<title>Cisco Switchport Report</title>\n")
            html_file.write("<style>\n* { padding: 8px; margin: 0; border: 0px; border-spacing: 0px; }\ntr { border-bottom: 1px solid #ccc; }\ntr:first-child { font-weight: bold; }\ntr:nth-child(odd) { background-color: #f2f2f2; }\n</style>\n")
            html_file.write("</head>\n<body>\n<table>\n<tr>\n<td>Hostname</td>\n<td>Interface</td>\n<td>Status</td>\n<td>Description</td>\n<td>MAC Address</td>\n<td>VLAN</td>\n<td>IP Address</td>\n</tr>\n")

            for ip in input_ips:

                conn = {
                    "host": str(ip),
                    "username": cisco_user,
                    "password": cisco_pass,
                    "device_type": "cisco_ios",
                }

                try:
                    net_connect = Netmiko(**conn)
                    vers = net_connect.send_command('show version')
                except:
                    print(f"Error Connecting to {str(ip)}") 
                else:
                    hostname = net_connect.find_prompt().split('#')[0]
                    if "Nexus" in vers:
                        int_list = net_connect.send_command('show interface brief')
                    else:
                        int_list = net_connect.send_command('show ip interface brief')
                    for j in int_list.splitlines():
                        if "down" not in j and "up" in j:
                            status = "up"
                        else:
                            status = "down"
                        desc = mac_add = vlan_id = vendor = ip_add = " "                         
                        int_conf = net_connect.send_command("show run int "+j.split()[0])
                        if "mode trunk" not in int_conf:
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
                                report_writer.writerow([hostname, j.split()[0], status, desc, mac_add, vlan_id, ip_add])
                                html_file.write("<tr>\n<td>"+hostname+"</td>\n<td>"+j.split()[0]+"</td>\n<td>"+status+"</td>\n<td>"+desc+"</td>\n<td>"+mac_add+"</td>\n<td>"+vlan_id+"</td>\n<td>"+ip_add+"</td>\n</tr>\n")
                    print(f"Process completed on {str(ip)}")
                    net_connect.disconnect()
            html_file.write("</table>\n</body>\n</html>")

main()
print("Port report has been generated")
