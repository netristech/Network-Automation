#!/usr/bin/env python

#import modules
import csv
import os
import platform
import subprocess
import ipaddress
from datetime import datetime
from multiprocessing import Pool

def ping(ip):
    if platform.system().lower() == 'windows':
        opt = '-n'
    else:
        opt = '-c'
    command = ['ping', opt, '1', ip]
    if subprocess.call(command) == 0:
        return ip

def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Get subnets from user
    while True:
        try:
            subnets = input("Enter a space delimited list of subnets (in CIDR notation) to scan: ").split()
            for i in range(0, len(subnets)):
                subnets[i] = ipaddress.IPv4Network(subnets[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break

    if len(subnets) > 0:
        pool = Pool(8)

        with open(f'{os.getcwd()}/scan_{timestamp}.csv', 'w') as csv_file:
            report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            report_writer.writerow(['subnet', 'alive host count'])

            # Try to ping hosts in subnets
            for subnet in subnets:
                count = 0
                ips = []
                for ip in ipaddress.ip_network(subnet).hosts():
                    ips.append(str(ip))
                count = len([x for x in pool.map(ping, ips) if x is not None])
                report_writer.writerow([subnet, count])

if __name__ == "__main__":
    main()