#!/usr/bin/env python

#import modules
import csv
import os
import ipaddress
import pexpect
import sys
from datetime import datetime
from getpass import getpass
#from netmiko import Netmiko
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
            report_writer.writerow(['IP Address', 'Hostname','Serial Number', 'VLAN ID', 'IP Address'])
                
            def tn_conn(ip):
                ret = [ip, 'Failed', '', '', '']
                try:
                    tn = pexpect.spawn(f'telnet {i p}', encoding='utf-8')
                    tn.expect('Username: ')
                    tn.sendline(access_user)
                    tn.expect('Password: ')
                    tn.sendline(access_pass)
                    tn.expect('.*\#')
                    tn.sendline('term len 0')
                    tn.expect('.*\#')
                except:
                    print(f'Telnet connection to {ip} failed.')
                    return ret
                else:
                    #Get Port Info
                    log_file = open(os.getcwd() + '/log_file', 'w')
                    tn.logfile = log_file
                    tn.sendline('show run | inc hostname')
                    tn.expect('.*\#')
                    tn.sendline('show inv | inc SN:')
                    tn.expect('.*\#')
                    tn.sendline('sh ip int bri | inc Vlan')
                    tn.expect('.*\#')
                    data = Path(os.getcwd() + '/log_file').read_text()
                    '''
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
                    '''
                    #Close out log file and telnet session
                    log_file.close()
                    #os.remove(os.getcwd() + '/log_file')
                    tn.close()
                    #return ret   

            for ip in dev_ips:

                try:
                    row = tn_conn(ip)
                    report_writer.writerow(row)                    
                except:
                    print(f"Failed to gather information for {ip}.")
                    report_writer.writerow([ip, 'Failed', '', '', ''])

if __name__ == "__main__":
    main()