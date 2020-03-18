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

    axl_wsdl = "/root/axlsqltoolkit/AXLAPI.wsdl"
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
    print("Gathering phone names. . .")
    phones = []
    try:
        #resp = axl_service.listPhone(searchCriteria={'name': '%', 'devicePoolName': 'US_DAYT%'}, returnedTags={'name': ''})
        resp = axl_service.listPhone(searchCriteria={'name': '%', 'devicePoolname': 'US_BETHPA%'}, returnedTags={'name': ''})
    except Fault:
        show_history()
    for phone in resp['return'].phone:
        phones.append(phone.name)

    # Gather additional phone information
    #key = {}
    with open(f'/root/cm_forward_{timestamp}.csv', 'w') as csv_file:#, open('/root/key.csv', newline='') as key_file:
        
        # Parse key file and store contents in dictionary
        #key_reader = csv.reader(key_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #for line in key_reader:
            #key.update({ line[0]: { "key": line[1] } })
        
        # Seed CSV report file with column headers
        report_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        report_writer.writerow(['Name', 'Extension', 'Phone IP', 'Location', 'Current ForwardAll CSS', 'Proposed ForwardAll CSS'])

        print("Generating Report. . .")
        for phone in phones:

            # Set important variables for each phone
            try:
                resp = axl_service.getPhone(name=phone)
            except Fault:
                show_history()
            else:      
                name = resp['return'].phone.description
                phone_loc = resp['return'].phone.locationName._value_1
                if hasattr(resp['return'].phone.lines, 'line'):
                    if resp['return'].phone.lines.line[0].dirn.routePartitionName._value_1 not in ("", " ", None):
                        phone_rpn = resp['return'].phone.lines.line[0].dirn.routePartitionName._value_1
                    else:
                        phone_rpn = 'unknown'
                    phone_pat = resp['return'].phone.lines.line[0].dirn.pattern
                    try:
                        resp = axl_service.getLine(routePartitionName=phone_rpn, pattern=phone_pat)
                    except Fault:
                        show_history()
                    else:
                        forward_css = resp['return'].line.callForwardAll.callingSearchSpaceName._value_1                    
                else:
                    phone_rpn = phone_pat = forward_css = ""

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
            '''loc_key = notes = ""
            matches = []
            for k in key:
                if ipaddress.ip_network(f"{phone_ip}/32").subnet_of(ipaddress.ip_network(k)):
                    loc_key = key[k]['key']
            if loc_key == "":
                notes = "Device not in voice VLAN / subnet! "
            else:
                if not phone_css.startswith(f"{loc_key}_"):
                    matches.append("Phone CSS ")
                if not phone_devpool.startswith(f"{loc_key}_"):
                    matches.append("Device Pool ")
                if (phone_rpn != "" and not phone_rpn.startswith(f"{loc_key}_")):
                    matches.append("Route Partition ")
                if phone_loc != loc_key:
                    matches.append("Phone location ")
                if line_css not in ("", " ", None, phone_css):
                    matches.append("Line CSS ")
                if len(matches) > 0:
                    notes += f"Inconsistent configuration found in: {matches}, expected location: {loc_key}. "
'''
            # Write results to CSV file
            new_css = "US_BETHPA_LongDistance"
            if forward_css in (new_css, "", None):
                new_css = "No Change"
            report_writer.writerow([name, phone_pat, phone_loc, phone_ip, forward_css, new_css])

main()
print("Report has been generated")
