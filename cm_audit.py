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
    phones = []
    try:
        resp = axl_service.listPhone(searchCriteria={'name': '%', 'devicePoolName': 'US_DAYT%'}, returnedTags={'name': ''})
    except Fault:
        show_history()
    for phone in resp['return'].phone:
        phones.append(phone.name)

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

        for phone in phones:

            # Set important variables for each phone
            try:
                resp = axl_service.getPhone(name=phone)
            except Fault:
                show_history()
            else:
                if phone.startswith('SEP'):
                    mac_address = phone[3:]
                else:
                    mac_address = 'unknown'            
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
                    phone_rpn = phone_pat = phone_mask = line_css = ""

            # Get IP addresses for all phones in list
            cm_select_criteria = {
                'MaxReturnedDevices': '1',
                'DeviceClass': 'Phone',
                'Model': '255',
                'Status': 'Any',
                'NodeName': '',
                'SelectBy': 'Name',
                'SelectItems': {
                    'item': phone
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
            
            # Check if device IP is in proper subnet and set location key
            loc_key = notes = ""
            for k in key:
                if ipaddress.ip_network(f"{phone_ip}/32").subnet_of(ipaddress.ip_network(k)):
                    loc_key = key[k]['key']
            if loc_key == "":
                notes = "Device not in voice VLAN / subnet! "
            elif not phone_css.startswith(f"{loc_key}_") or \
            not phone_devpool.startswith(f"{loc_key}_") or \
            (phone_rpn != "" and not phone_rpn.startswith(f"{loc_key}_")) or \
            phone_loc != loc_key:
                notes = "Configuration inconsistent! "
            if line_css not in ("", "unknown", " ", None):
                notes += "Line CSS configuration found! "

            # Write results to CSV file                                
            report_writer.writerow([phone, phone_ip, mac_address, phone_pat, phone_desc, phone_css, phone_devpool, phone_loc, phone_rpn, phone_mask, line_css, notes])

main()
