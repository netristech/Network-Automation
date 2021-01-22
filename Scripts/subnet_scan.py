#!/usr/bin/env python

#import modules
import os
import sys
import subprocess
import ipaddress
from multiprocessing import Pool

def ping(ip):
    # Execute command and return ip if return code is zero
    with open(os.devnull, 'w') as devnull:
        command = ['ping', '-c', '1', ip]
        if subprocess.call(command, stdout=devnull, stderr=devnull) == 0:
            return ip

def main():
    #timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    subnet = sys.argv[1]
    pool = Pool(8)

    # Try to ping hosts in subnets
    ips = []
    for ip in ipaddress.ip_network(subnet).hosts():
        ips.append(str(ip))
    count = len([x for x in pool.map(ping, ips) if x is not None])
    print(count)

if __name__ == "__main__":
    main()