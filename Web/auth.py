#!/usr/bin/env python

#import modules
import sys
from getpass import getpass
from netmiko import Netmiko

auth_username = sys.argv[1]
auth_password = sys.argv[2]

def main():
                
    # Create connection object for Netmiko
    conn = {
        "host": '172.30.190.62',
        "username": auth_username,
        "password": auth_password,
        "device_type": "cisco_ios",
    }

    # Attempt connection
    try:
        net_connect = Netmiko(**conn)
    except:
        print("false")
    else:
        print("true")

if __name__ == "__main__":
    main()
