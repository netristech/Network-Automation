#!/usr/bin/env python

#imports
from __future__ import print_function
import ipaddress
import csv
from multiprocessing import Pool
from getpass import getpass
from netmiko import Netmiko

def main():
    def trace(ipaddr):
        report_writer.writerow([ipaddr, net_connect.send_command('traceroute '+ipaddr)])

    while True:
        try:
            source_dev = ipaddress.IPv4Address(raw_input("Source device to originate traceroute: "))
        except:
            pass
        else:
            break
    while True:
        try:
            dest_ips = raw_input("Destination IP or IPs (space delimited): ").split(" ")
            for i in range(0, len(dest_ips)):
                dest_ips[i] = ipaddress.IPv4Address(dest_ips[i])
        except:
            pass
        else:
            break
    while True:
        print("Enter user login credentials for source device below:")
        login_user = raw_input("username: ")
        login_pass = getpass()
        conn = {
            "host": str(source_dev),
            "username": login_user,
            "password": login_pass,
            "device_type": "cisco_ios",
        }
        try:
            net_connect = Netmiko(**conn)
            hostname = net_connect.find_prompt().split('#')[0]
        except:
            pass
        else:
            break
    report_writer = csv.writer("trace_report_"+hostname, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    report_writer.writerow(['Trace Report from '+hostname+"("str(source_dev)+")", ''])
    report_writer.writerow(['Destination', 'Results'])
    if __name__ == '__main__':
        with Pool(10) as pool:
            pool.map(trace, list(dest_ips))

main()