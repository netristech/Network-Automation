#!/usr/bin/env python

#imports
import ipaddress
import csv
import re
import sys
import os
from multiprocessing import Pool
from datetime import datetime
from getpass import getpass
from netmiko import Netmiko