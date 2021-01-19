#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json
import ipaddress
import socket
from multiprocessing import Pool

subnets = ['172.31.100.0/26']
all_ips = []

def main():
    print(json.dumps(inventory(), sort_keys=True, indent=2))

def inventory():
    pool = Pool(8)
    get_ips()
    devs = [x for x in pool.map(ssh_open, all_ips) if x is not None]

    return {
        'all': {
            'hosts': devs,
            'vars': {},
        },
        '_meta': {},
    }

def get_ips():
    for subnet in subnets:
        for ip in ipaddress.ip_network(subnet).hosts():
            all_ips.append(str(ip))

def ssh_open(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, 22))
    except:
        pass
    else:
        if result == 0:
            sock.close()
            return ip
    
if __name__ == '__main__':
    main()