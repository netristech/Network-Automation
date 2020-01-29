#!/usr/bin/env python

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
from getpass import getpass 
 
#disable_warnings(InsecureRequestWarning)

#get session variables from user
server = input("CUCM device IP to connect to: ")
username = input("CUCM Username: ")
password = getpass("CUCM Password: ")

# Build Client Object for AXL Service
history = HistoryPlugin()

axl_wsdl = '/root/scripts/axlsqltoolkit/AXLAPI.wsdl'
axl_location = f'https://{server}:8443/axl/'
axl_binding = '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding'

axl_session = Session()
axl_session.verify = False
axl_session.auth = HTTPBasicAuth(username, password)

axl_transport = Transport(cache=SqliteCache(), session=axl_session, timeout=20)
axl_client = Client(wsdl=axl_wsdl, transport=axl_transport, plugins=[history])
axl_service = axl_client.create_service(axl_binding, axl_location)

wsdl = f'https://{server}:8443/realtimeservice2/services/RISService70?wsdl'

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
try:
    resp = axl_service.listPhone(searchCriteria={'name': 'SEP%'}, returnedTags={'name': ''})
except Fault:
    show_history()

#print(resp)

for phone in resp['return'].phone:
    items.append(phone.name)
#    print(phone.name)

cm_select_criteria = {
    'MaxReturnedDevices': '1',
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
#else:
#    print(resp)

node = resp.SelectCmDeviceResult.CmNodes.item
for node in node:
    if len(node.CmDevices.item) > 0:
        for item in node.CmDevices.item:
            for ip in item.IPAddress.item:
                print(f"{item.Name} {ip.IP}")

