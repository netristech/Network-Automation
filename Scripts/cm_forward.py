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
        resp = axl_service.listPhone(searchCriteria={'name': 'SEP7001B5DB1366'}, returnedTags={'name': ''})
        #resp = axl_service.listPhone(searchCriteria={'name': '%'}, returnedTags={'name': ''})
    except Fault:
        show_history()
    for phone in resp['return'].phone:
        phones.append(phone.name)

    # Gather additional phone information
    for phone in phones:

        # Set important variables for each phone
        try:
            resp = axl_service.getPhone(name=phone)
        except Fault:
            show_history()
        else:
            if hasattr(resp['return'].phone.lines, 'line'):
                if resp['return'].phone.lines.line[0].dirn.routePartitionName._value_1 not in ("", " ", None):
                    phone_rpn = resp['return'].phone.lines.line[0].dirn.routePartitionName._value_1
                else:
                    phone_pat = resp['return'].phone.lines.line[0].dirn.pattern
                    try:
                        resp = axl_service.getLine(routePartitionName=phone_rpn, pattern=phone_pat)
                    except Fault:
                        show_history()
                    else:
                        print(resp)

main()
