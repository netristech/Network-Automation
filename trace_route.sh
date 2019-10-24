#!/bin/bash

if [ ! -z "$1" ]; then
    traceroute -V > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        sudo apt-get install -y -qq traceroute > /dev/null 2>&1
    fi
    sudo traceroute -4 -n -I $1 | egrep -o "[[:digit:]]{1,2}.[[:blank:]]([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}"
fi