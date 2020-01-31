#!/usr/bin/env python

import ipaddress
from getpass import getpass
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
#from urllib3 import disable_warnings
#from urllib3.exceptions import InsecureRequestWarning
from lxml import etree
 
#disable_warnings(InsecureRequestWarning)

#get session variables from user
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

items = []

# Get a list of all phone names and store in a list
try:
#    resp = axl_service.getPhone(name='SEPD4AD71BF32E0')
    resp = axl_service.listPhone(searchCriteria={'name': '%'}, returnedTags={'name': ''})
except Fault:
    show_history()
for phone in resp['return'].phone:
    items.append(phone.name)

# Get IP addresses for all phones in list
cm_select_criteria = {
    'MaxReturnedDevices': '100',
    'DeviceClass': 'Phone',
    'Model': '255',
    'Status': 'Any',
    'NodeName': '',
    'SelectBy': 'Name',
    'SelectItems': {
        'item': items
    },
    'Protocol': 'Any',
    'DownloadStatus': 'Any'
}

try:
    resp = client.service.selectCmDeviceExt(CmSelectionCriteria=cm_select_criteria, StateInfo='')
except Fault:
    show_history()
else:
    node = resp.SelectCmDeviceResult.CmNodes.item
    for node in node:
        print(f"{node.cmDevices.item.name} {node.cmDevices.item.IPAddress.item.IP}")
'''
        if len(node.CmDevices.item) > 0:
            for item in node.CmDevices.item:
                for ip in item.IPAddress.item:
                    print(f"{item.Name} {ip.IP}")

# Get Additional phone and line information
#phone_uuid = resp['return'].phone.uuid.lstrip('{').rstrip('}')
#line_uuid = resp['return'].phone.lines.line[0].uuid.lstrip('{').rstrip('}')
#dirn_uuid = resp['return'].phone.lines.line[0].dirn.uuid.lstrip('{').rstrip('}')
#rpn_uuid = resp['return'].phone.lines.line[0].dirn.routePartitionName.uuid
rpn = resp['return'].phone.lines.line[0].dirn.routePartitionName._value_1
pat = resp['return'].phone.lines.line[0].dirn.pattern

try:
    resp = axl_service.getLine(routePartitionName=rpn, pattern=pat)
except Fault:
    show_history()
#print(resp)
print(resp['return'].line.shareLineAppearanceCssName._value_1)

'''