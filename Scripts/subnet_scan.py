#!/usr/bin/env python

#import modules
import csv
import os
import sys
import platform
import subprocess
import ipaddress
from datetime import datetime
from multiprocessing import Pool

def ping(ip):
    # Determine platform and set argument accordingly
    if platform.system().lower() == 'windows':
        opt = '-n'
    else:
        opt = '-c'

    # Execute command and return ip if return code is zero
    with open(os.devnull, 'w') as devnull:
        command = ['ping', opt, '1', ip]
        if subprocess.call(command, stdout=devnull, stderr=devnull) == 0:
            return ip

def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    subnets = sys.argv[1]

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