#!/usr/bin/env python

# Import Libraries
import os
import ipaddress
import csv
from getpass import getpass
from datetime import datetime
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from lxml import etree

def main():

    # Get session variables from user
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    server = input("CUCM device IP to connect to: ")
    username = input("CUCM Username: ")
    password = getpass("CUCM Password: ")

    # Build Client Object for AXL Service
    history = HistoryPlugin()

    axl_wsdl = "/root/scripts/axlsqltoolkit/AXLAPI.wsdl"
    axl_location = f"https://{server}:8443/axl/"
    axl_binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"

    axl_session = Session()
    axl_session.verify = False
    axl_session.auth = HTTPBasicAuth(username, password)

    axl_transport = Transport(cache=SqliteCache(), session=axl_session, timeout=20)
    axl_client = Client(wsdl=axl_wsdl, transport=axl_transport, plugins=[history])
    axl_service = axl_client.create_service(axl_binding, axl_location)

    wsdl = f"https://{server}:8443/realtimeservice2/services/RISService70?wsdl"

    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(username, password)

    transport = Transport(cache=SqliteCache(), session=session, timeout=20)
    history = HistoryPlugin()
    client = Client(wsdl=wsdl, transport=transport, plugins=[history])

    def show_history():
        for hist in [history.last_sent, history.last_received]:
            print(etree.tostring(hist["envelope"], encoding="unicode", pretty_print=True))

    # Get a list of all phone names and store in a list
    items = []
    try:
        resp = axl_service.listPhone(searchCriteria={'name': '%', 'devicePoolName': 'US_DAYTFL%'}, returnedTags={'name': ''})
    except Fault:
        show_history()
    for phone in resp['return'].phone:
        items.append(phone.name)

    # Gather additional phone information
    key = {}
    with open(f'{os.getcwd()}/cm_audit_{timestamp}.csv', 'w') as csv_file, open(f'{os.path.dirname(os.getcwd())}/key.csv', newline='') as key_file:
        
        # Parse key file and store contents in dictionary
        key_reader = csv.reader(key_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in key_reader:
            key.update({ line[0]: { "key": line[1] } })
        
        # Seed CSV report file with column headers
        report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        report_writer.writerow(['Name', 'IP Address', 'MAC Address', 'Extension', 'Description', 'Phone CSS', 'Device Pool', 'Location', 'Route Parition', 'External Mask', 'Line CSS', 'Notes'])

        for item in items:

            # Set important variables for each phone
            if item.startswith('SEP'):
                mac_address = item[3:]
            else:
                mac_address = 'unknown'            
            try:
                resp = axl_service.getPhone(name=item)
            except Fault:
                show_history()
            else:
                phone_desc = resp['return'].phone.description
                #phone_model = resp['return'].phone.model
                phone_css = resp['return'].phone.callingSearchSpaceName._value_1
                phone_devpool = resp['return'].phone.devicePoolName._value_1
                phone_loc = resp['return'].phone.locationName._value_1
                if hasattr(resp['return'].phone.lines, 'line'):
                    phone_rpn = resp['return'].phone.lines.line[0].dirn.routePartitionName._value_1
                    phone_pat = resp['return'].phone.lines.line[0].dirn.pattern
                    phone_mask = resp['return'].phone.lines.line[0].e164Mask
                    try:
                        resp = axl_service.getLine(routePartitionName=phone_rpn, pattern=phone_pat)
                    except Fault:
                        show_history()
                    else:
                        line_css = resp['return'].line.shareLineAppearanceCssName._value_1                    
                else:
                    phone_rpn = phone_pat = phone_mask = line_css = 'unknown'

            # Get IP addresses for all phones in list
            cm_select_criteria = {
                'MaxReturnedDevices': '1',
                'DeviceClass': 'Phone',
                'Model': '255',
                'Status': 'Any',
                'NodeName': '',
                'SelectBy': 'Name',
                'SelectItems': {
                    'item': item
                },
                'Protocol': 'Any',
                'DownloadStatus': 'Any'
            }

            try:
                resp = client.service.selectCmDeviceExt(CmSelectionCriteria=cm_select_criteria, StateInfo='')
            except Fault:
                show_history()
            else:
                nodes = resp.SelectCmDeviceResult.CmNodes.item
                for node in nodes:
                    if len(node.CmDevices.item) > 0:
                        for item in node.CmDevices.item:
                            for ip in item.IPAddress.item:
                                phone_ip = ip.IP
            
            # Write results to CSV file                                
            report_writer.writerow([item, phone_ip, mac_address, phone_pat, phone_desc, phone_css, phone_devpool, phone_loc, phone_rpn, phone_mask, line_css, notes])

main()