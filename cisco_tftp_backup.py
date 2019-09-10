#! /usr/bin/env python
from netmiko import Netmiko
from getpass import getpass
from datetime import datetime

tftphost = raw_input("TFTP Server IP: ")
ciscouser = raw_input("Login username: ")
ciscopass = getpass()

with open('/home/brian/ips') as file:
  for line in file:

    conn = {
      "host": line,
      "username": ciscouser,
      "password": ciscopass,
      "device_type": "cisco_ios",
    }

    try:
      net_connect = Netmiko(**conn)
    except:
      print "unable to connect to "+line
    else:
      timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
      hostname = net_connect.find_prompt().split('#')[0]
      copytftp = "copy start tftp://"+tftphost+"/"+hostname+"-config-"+timestamp
      output = net_connect.send_command_timing(copytftp)
      while (':' in output) or ('?' in output):
        output = net_connect.send_command_timing("\n")
      net_connect.disconnect()
      print hostname+" configuration successfully backed up"
