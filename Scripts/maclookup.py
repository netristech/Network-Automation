#!/usr/bin/env python

import argparse
from mac_vendor_lookup import MacLookup

parser = argparse.ArgumentParser()
parser.add_argument('mac')
args = parser.parse_args()
print(MacLookup().lookup(args.mac))
