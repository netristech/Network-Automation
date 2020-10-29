#!/usr/bin/env python

#import modules
import csv
import os
import ipaddress
import pexpect
import sys
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko
from pathlib import Path    

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
            input_macs = input("Enter a space delimited list of IPs: ").split()
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break
    
    if len(input_ips) > 0:

        # gather username and password
        core_user = input("Core Switch Username: ")
        core_pass = getpass("Core Switch Password: ")
        access_user = input("Access Switch Username (Leave Blank if the Same): ")
        access_pass = getpass("Access Switch Password (Leave Blank if the Same): ")
        if access_user == '':
            access_user = core_user
        if access_pass == '':
            access_pass = core_pass
        
        # Open csv file for write operation
        with open(f'{os.getcwd()}/log_{timestamp}.csv', 'w') as csv_file:
            report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            report_writer.writerow(['MAC Address','Switch', 'Port'])
            for mac in input_macs:
                # Reset variables   
                try:
                    tn = pexpect.spawn(f'telnet {dev_ip}', encoding='utf-8')
                    tn.expect('Username: ')
                    tn.sendline(access_user)
                    tn.expect('Password: ')
                    tn.sendline(access_pass)
                    tn.expect('.*\#')
                except:
                    print(f"Connection to {switch_ip} failed.")
                    report_writer.writerow([mac, 'Failed to get info', ''])
                else:
                    #Get Info
                    log_file = open(os.getcwd() + '/log_file', 'w')
                    tn.logfile = log_file
                    tn.sendline('show run | inc hostname')
                    tn.expect('.*\#')
                    tn.sendline(f'show mac add | inc {mac}')
                    tn.expect('.*\#')
                    data = Path(os.getcwd() + '/log_file').read_text()
                    if data != '':
                        hostname = data.splitlines()[2].split()[1]
                        port = data.splitlines()[5].split()[3]
                    #print(f'{hostname} {port}')

                    #Close out log file and telnet session
                    log_file.close()
                    os.remove(os.getcwd() + '/log_file')
                    tn.close()

                    #Write CSV File
                    report_writer.writerow([mac, hostname, port])

if __name__ == "__main__":
    main()