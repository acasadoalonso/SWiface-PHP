#!/bin/bash
# usage: ./genconfig.sh <comp-id>   where <comp-id> is the CSGP competition ID 
if [ -n "$CONFIGDIR" ]; then
    echo "CONFIGDIR is set to: $CONFIGDIR"
    python3 gen_swsconfig.py  --comp-id $1 --config-dir $CONFIGDIR
else
    echo "CONFIGDIR is not set, use the default /etc/local directory"
    python3 gen_swsconfig.py  --comp-id $1 --config-dir /etc/local 
fi

python3 genconfig.py
