#!/bin/sh
cd /nfs/OGN/SWdata/SGP/DAY$1
rm $3.$2.igc 
grep "FLARM "$2 * | sort -k 3 | python /var/www/html/SWS/genIGC.py $2 > $3.$2.igc
