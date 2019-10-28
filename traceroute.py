#!/usr/bin/env python

#imports
from __future__ import print_function
import sys
import os
import re
import ipaddress
import csv

def main():
    while True:
        try:
            dest_ips = raw_input("Destination IP or IPs (space delimited): ").split(" ")
            for i in range(0, len(dest_ips)):
                dest_ips[i] = ipaddress.IPv4Address(u""+dest_ips[i])
        except:
            pass
        else:
            break
    with open("trace_report.csv", "w") as csvfile:
        report_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        report_writer.writerow(['Destination', 'Results'])
        sys.stdout.write("Please wait while the report is being generated ")
        sys.stdout.flush()
        for ip in list(dest_ips):
            os.system("sudo "+os.getcwd()+"/trace_route.sh "+str(ip))
            with open (os.getcwd()+"/temp_trace.txt") as output:
                report_writer.writerow([str(ip), output.read()])
                sys.stdout.write(". ")
                sys.stdout.flush()

main()
print("\nReport generation complete!")
