#!/usr/bin/env python

#import modules
import csv
import os
import ipaddress
import pexpect
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path    

def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # get list of IPs to perform ARP lookup against
    while True:
        try:
            dev_ips = input("Enter a space delimited list of IPs: ").split()
            for i in range(0, len(dev_ips)):
                dev_ips[i] = ipaddress.IPv4Address(dev_ips[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break
    
    if len(dev_ips) > 0:

        # gather username and password
        access_user = input("Switch Username: ")
        access_pass = getpass("Switch Password: ")
        
        # Open csv file for write operation
        with open(f'{os.getcwd()}/report_{timestamp}.csv', 'w') as csv_file:
            report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            report_writer.writerow(['Hostname','Serial Number', 'VLAN ID', 'IP Address'])
                
            def tn_conn(ip):
                data = ''
                try:
                    tn = pexpect.spawn(f'telnet {ip}', encoding='utf-8')
                    tn.expect('Username: ')
                    tn.sendline(access_user)
                    tn.expect('Password: ')
                    tn.sendline(access_pass)
                    tn.expect('.*\#')
                    tn.sendline('term len 0')
                    tn.expect('.*\#')
                except:
                    print(f'Connection to {ip} failed.')
                    yield ['Failed', '', '', '']
                    pass
                else:
                    #Get Info
                    log_file = open(os.getcwd() + '/log_file', 'w')
                    tn.logfile = log_file
                    tn.sendline('show run | inc hostname')
                    tn.expect('.*\#')
                    tn.sendline('show inv | inc SN:')
                    tn.expect('.*\#')
                    tn.sendline('sh ip int bri | inc Vlan')
                    tn.expect('.*\#')
                    data = Path(os.getcwd() + '/log_file').read_text()
                    hostname = data.splitlines()[2].split()[1]
                    serial_num = data.splitlines()[5].split()[-1]
                    vlans = data[data.find("Vlan"):].splitlines()
                    for i in range(len(vlans)):
                        if vlans[i].split()[1] != "unassigned":
                            vlan = vlans[i].split()[0]
                            ip_addr = vlans[i].split()[1]
                            if i == 0:
                                yield [hostname, serial_num, vlan, ip_addr]
                            else:
                                yield ['', '', vlan, ip_addr]                       
                #Close out log file and telnet session
                log_file.close()
                os.remove(os.getcwd() + '/log_file')
                tn.close()

            for ip in dev_ips:

                try:
                    for row in tn_conn(ip):
                        report_writer.writerow(row)                    
                except:
                    print(f"Failed to gather information for {ip}.")
                    report_writer.writerow(['Failed', '', '', ''])

if __name__ == "__main__":
    main()