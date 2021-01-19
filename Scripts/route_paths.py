#!/usr/bin/env python

#imports
from __future__ import print_function
import sys
import re
import ipaddress
import csv
from multiprocessing import Process
from getpass import getpass
from netmiko import Netmiko

def main():
    while True:
        try:
            source_dev = ipaddress.IPv4Address(u""+raw_input("Source device to originate traceroute: "))
        except:
            pass
        else:
            break
    while True:
        try:
            dest_ips = raw_input("Destination IP or IPs (space delimited): ").split(" ")
            for i in range(0, len(dest_ips)):
                dest_ips[i] = ipaddress.IPv4Address(u""+dest_ips[i])
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
    with open("trace_report_"+hostname+".csv", "w") as csvfile:
        report_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        report_writer.writerow(['Trace Report from '+hostname+"("+str(source_dev)+")", ''])
        report_writer.writerow(['Destination', 'Results'])
        sys.stdout.write("Please wait while the report is being generated ")
        sys.stdout.flush()
        for ip in list(dest_ips):
            output = net_connect.send_command_timing("traceroute "+str(ip)+"\n", expect_string=hostname)
            #while (':' in output) or ('?' in output):
                #output = net_connect.send_command_timing("\n")
            report_writer.writerow([str(ip), output.strip()])
            sys.stdout.write(". ")
            sys.stdout.flush()
            output = ""
    net_connect.disconnect()

if __name__ == "__main__":
    main()
    
print("\nReport generation complete!")
