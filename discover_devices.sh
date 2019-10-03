#!/bin/bash

if [ ! -z "$1" ] && [ ! -z "$2" ]; then
    nmap -V > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        sudo apt-get install -y -qq nmap > /dev/null 2>&1
    fi
    oct=$(echo $1 | cut -d'.' -f1)
    sudo nmap -Pn -sT -p 22 --open -n $1 | grep -o "$oct.*" > $2
fi