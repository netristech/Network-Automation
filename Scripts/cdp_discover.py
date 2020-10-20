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
    
    # get device IP for SSH connection
    while True:
        try:
            dev_ip = input("IP of device to connect to: ")
            dev_ip = ipaddress.IPv4Address(dev_ip)
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break

    # get list of IPs to perform ARP lookup against
    while True:
        try:
            input_ips = input("Enter a space delimited list of IPs: ").split()
            for i in range(0, len(input_ips)):
                input_ips[i] = ipaddress.IPv4Address(input_ips[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break
    
    if len(input_ips) > 0:

        # gather username and password
        cisco_user = input("Device Username: ")
        cisco_pass = getpass("Device Password: ")
        
        # Open csv file for write operation
        with open(f'{os.getcwd()}/cdp_{timestamp}.csv', 'w') as csv_file:
            report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            report_writer.writerow(['IP Address', 'Switch', 'Port'])
                
            # Create connection object for Netmiko
            conn = {
                "host": dev_ip,
                "username": cisco_user,
                "password": cisco_pass,
                "device_type": "cisco_ios",
            }

            # Attempt connection
            try:
                net_connect = Netmiko(**conn)
                vers = net_connect.send_command('show version')
            except:
                print(f"Connection to {dev_ip} failed.")
            else:
                for ip in input_ips:
                    try:
                        net_connect.send_command(f'ping {ip}')
                        mac = net_connect.send_command(f'sho ip arp {ip} | inc {ip}').split()[2]
                        port = net_connect.send_command(f'sho mac add | inc {mac}').split()[7]
                        cdp = net_connect.send_command(f'sho cdp nei int {port} det')
                        switch_ip = cdp[cdp.find("Mgmt address(es):"):].splitlines()[1].split(':')[1].strip()
                        user = input("Switch Username: ")
                        passw = getpass("Switch Password: ")
                        new_conn = {
                            "host": switch_ip,
                            "username": user,
                            "password": passw,
                            "device_type": "cisco_ios",
                        }
                        try:
                            net_connect = Netmiko(**new_conn)
                            vers = net_connect.send_command('show version')
                        except:
                            print(f"Connection to {switch_ip} failed.")
                        else:
                            switch = net_connect.find_prompt().split('#')[0]
                            port = net_connect.send_command(f'sho mac add | inc {mac}').split()[7]
                    except:
                        print(f"Failed to gather information for {ip}.")
                    else:
                        report_writer.writerow([ip, switch, port])
                net_connect.disconnect()

if __name__ == "__main__":
    main()