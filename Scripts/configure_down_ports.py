#!/usr/bin/env python

#import modules
import ipaddress
from getpass import getpass
from netmiko import Netmiko

def main():

    # Get device(s) to connect to
    while True:
        try:
            devs = input("Enter a space delimited list of device IPs: ").split()
            for i in range(0, len(devs)):
                devs[i] = ipaddress.IPv4Address(devs[i])
        except:
            if input("Invalid data entered. Press any key to continue or 'q' to quit. ") == 'q':
                exit()
        else:
            break
    
    if len(devs) > 0:  
        
        # gather username and password
        cisco_user = input("Device Username: ")
        cisco_pass = getpass("Device Password: ")
        
        # Loop through devices
        for dev in devs:
                
            # Create connection object for Netmiko
            conn = {
                "host": str(dev),
                "username": cisco_user,
                "password": cisco_pass,
                "device_type": "cisco_ios",
            }

            # Attempt connection
            try:
                net_connect = Netmiko(**conn)
                vers = net_connect.send_command('show version')
            except:
                pass
            else:
                # Special handling for Nexus
                if "Nexus" in vers:
                    command = 'show int brief | inc down'
                
                # Normal handling for IOS
                else:
                    command = 'show ip int brief | inc down'

                # Get list of down ports and configure as client access ports
                ports = net_connect.send_command(command).split()[0]
                for port in ports:
                    int_commands = [
                        f'interface {port}',
                        'switchport mode access',
                        'switchport access vlan 2',
                        'switchport voice vlan 10',
                        'spanning portfast',
                        'spanning link point',
                        'no logging event link',
                        'no snmp trap link'
                    ]
                    if port.startswith(('Eth', 'eth', 'Gig', 'gig', 'Fa', 'fa')):
                        output = net_connect.send_config_set(int_commands)
                        print(output)

main()
print("\nCompleted Successfully")
