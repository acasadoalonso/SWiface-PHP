#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import json
import time

tp1={"latitude": 42.3868, "longitude": 1.8683, "name": "LECD", "observationZone": "line", "type": "Start", "radius": 1000, "trigger":"Enter"}
tp2={"latitude": 42.5675, "longitude": -0.72566, "name": "LECI", "observationZone": "line", "type": "Start", "radius": 1000, "trigger":"Enter"}

tr1={"trackId": "FLRDDC1AC", "pilotName": "Angel Casado", "competitionId": "K5", "country": "ES", "aircraft": "Janus CE", "registration": "D-2520", "3dModel": "ventus2", "ribbonColors":["red"]} 
tr2={"trackId": "FLRDDE1FC", "pilotName": "Sergi Pujol", "competitionId": "SP", "country": "FR", "aircraft": "Duo Discus", "registration": "D-1234", "3dModel": "ventus2", "ribbonColors":["blue"]} 
tr3={"trackId": "FLRDDDB8B", "pilotName": "Luis Ferreira", "competitionId": "AA", "country": "ES", "aircraft": "Duo Discus", "registration": "EC-JAA", "3dModel": "ventus2", "ribbonColors":["green"]} 
ev1={"name": "QSGP La Cerdanya", "description": "Day 1", "taskType": "SailplaneGrandPrix", "startOpenTs": 0, "turnpoints": [tp1, tp2], "tracks": [tr1, tr2, tr3]} 
j=json.dumps(ev1, indent=4)
print j
