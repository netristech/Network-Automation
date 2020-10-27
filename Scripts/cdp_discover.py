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
            report_writer.writerow(['IP Address', 'Switch', 'Port'])
                
            # Create connection object for Netmiko
            conn = {
                "host": str(dev_ip),
                "username": core_user,
                "password": core_pass,
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

                    # Reset variables
                    switch_ip = ''
                    mac = ''
                    port = ''
                    cdp = ''

                    try:
                        net_connect.send_command(f'ping {ip} count 1')
                        mac = net_connect.send_command(f'sho ip arp {ip} | inc {ip}').split()[2]
                        port = net_connect.send_command(f'sho mac add | inc {mac}').split()[7]
                        cdp = net_connect.send_command(f'sho cdp nei int {port} det')
                        switch_ip = cdp[cdp.find("Mgmt address(es):"):].splitlines()[1].split(':')[1].strip()
                    except:
                        print(f"Failed to gather information for {ip}.")
                        report_writer.writerow([ip, 'Failed to get info', ''])
                    else:                    
                        try:
                            tn = pexpect.spawn(f'telnet {switch_ip}', encoding='utf-8')
                            tn.expect('Username: ')
                            tn.sendline(access_user)
                            tn.expect('Password: ')
                            tn.sendline(access_pass)
                            tn.expect('.*\#')
                        except:
                            print(f"Connection to {switch_ip} failed.")
                        else:
                            #Get Port
                            log_file = open(os.getcwd() + '/log_file', 'w')
                            tn.sendline(f'show mac add | inc {mac}')
                            tn.logfile_send = log_file
                            tn.expect('.*\#')
                            log_file.close()
                            log_file = open(os.getcwd() + '/log_file', 'r')
                            data = log_file.read()
                            log_file.close()
                            if data != '':
                                port = data.splitlines()[1].split()[3]

                            #Check port
                            log_file = open(os.getcwd() + '/log_file', 'w')
                            tn.sendline(f'show cdp neigh {port} det')
                            tn.logfile_send = log_file
                            tn.expect('.*\#')
                            log_file.close()
                            log_file = open(os.getcwd() + '/log_file', 'r')
                            data = log_file.read()
                            log_file.close()
                            if "Cisco" in data:
                                tn.close()
                                switch_ip = data[data.find("Mgmt address(es):"):].splitlines()[1].split(':')[1].strip()
                                try:
                                    tn = pexpect.spawn(f'telnet {switch_ip}', encoding='utf-8')
                                    tn.expect('Username: ')
                                    tn.sendline(access_user)
                                    tn.expect('Password: ')
                                    tn.sendline(access_pass)
                                    tn.expect('.*\#')
                                except:
                                    print(f"Connection to {switch_ip} failed.")
                                else:
                                    #Get Port
                                    log_file = open(os.getcwd() + '/log_file', 'w')
                                    tn.sendline(f'show mac add | inc {mac}')
                                    tn.logfile_send = log_file
                                    tn.expect('.*\#')
                                    log_file.close()
                                    log_file = open(os.getcwd() + '/log_file', 'r')
                                    data = log_file.read()
                                    log_file.close()
                                    port = data.splitlines()[1].split()[3]
                            
                            #Get hostname
                            log_file = open(os.getcwd() + '/log_file', 'w')
                            tn.sendline('show run | inc hostname')
                            tn.logfile_read = log_file
                            tn.expect('.*\#')
                            log_file.close()
                            log_file = open(os.getcwd() + '/log_file', 'r')
                            data = log_file.read()
                            log_file.close()
                            if data != '':
                                hostname = data.splitlines()[1].split()[1]
                            tn.close()

                            #Write CSV File
                            report_writer.writerow([ip, hostname, port])
                net_connect.disconnect()

if __name__ == "__main__":
    main()