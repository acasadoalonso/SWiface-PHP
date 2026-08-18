#!/bin/bash
# usage: ./genconfig.sh <comp-id>   where <comp-id> is the CSGP competition ID 
if [ -n "$CONFIGDIR" ]; then
    echo "CONFIGDIR is set to: $CONFIGDIR"
    python3 gen_swsconfig.py  --comp-id $1 --config-dir $CONFIGDIR
    chown www-data:www-data $CONFIGDIR/* 
else
    echo "CONFIGDIR is not set, use the default /etc/local directory"
    python3 gen_swsconfig.py  --comp-id $1 --config-dir /etc/local 
fi
# gen the config.py and config.php files
python3 genconfig.py
