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
            report_writer.writerow(['IP Address', 'MAC Address','Switch', 'Port'])
                
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
                def tn_conn(params):
                    #Set variables
                    ip = params[0]
                    switch_ip = params[1]
                    mac = params[2]
                    ret = [ip, 'Failed to get info', '', '']

                    try:
                        tn = pexpect.spawn(f'telnet {switch_ip}', encoding='utf-8')
                        tn.expect('Username: ')
                        tn.sendline(access_user)
                        tn.expect('Password: ')
                        tn.sendline(access_pass)
                        tn.expect('.*\#')
                        tn.sendline('term len 0')
                        tn.expect('.*\#')
                    except:
                        print(f'Telnet connection to {switch_ip} failed. {access_user}, {ip}, {mac}')
                        return ret
                    else:
                        #Get Port Info
                        log_file = open(os.getcwd() + '/log_file', 'w')
                        tn.logfile = log_file
                        tn.sendline('show run | inc hostname')
                        tn.expect('.*\#')
                        tn.sendline(f'show mac add | inc {mac}')
                        tn.expect('.*\#')
                        data = Path(os.getcwd() + '/log_file').read_text()
                        try:
                            hostname = data.splitlines()[2].split()[1]
                            port = data.splitlines()[5].split()[3]
                        except:
                            pass
                        else:                        
                            #Check Port
                            tn.sendline(f'show cdp neigh {port} det')
                            tn.expect('.*\#')
                            data = ''
                            data = Path(os.getcwd() + '/log_file').read_text()                           
                            if "Cisco" in data:
                                ret = [data[data.find("address(es):"):].splitlines()[1].split(':')[1].strip()]
                            else:
                                tn.sendline('show run | inc hostname')
                                tn.expect('.*\#')
                                data = ''
                                data = Path(os.getcwd() + '/log_file').read_text()
                                ret = [ip, mac, hostname, port]

                        #Close out log file and telnet session
                        log_file.close()
                        os.remove(os.getcwd() + '/log_file')
                        tn.close()
                        return ret   

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
                        switch_ip = cdp[cdp.find("address(es):"):].splitlines()[1].split(':')[1].strip()
                    except:
                        print(f"Failed to gather information for {ip}.")
                        report_writer.writerow([ip, 'Failed to ping', '', ''])
                    else:
                        row = tn_conn([ip, switch_ip, mac])
                        while len(row) == 1:
                            row = tn_conn([ip, row[0], mac])
                        report_writer.writerow(row)
                net_connect.disconnect()

if __name__ == "__main__":
    main()