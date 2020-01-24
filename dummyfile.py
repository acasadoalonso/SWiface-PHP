# --------------------------------------#
# -*- coding: UTF-8 -*-

# --------------------------------------#
def fixcoding(addr):
        if addr != None:
                addr=addr.replace('á', 'a')
                addr=addr.replace('à', 'a')
                addr=addr.replace('â', 'a')
                addr=addr.replace('Á', 'A')
                addr=addr.replace('é', 'e')
                addr=addr.replace('è', 'e')
                addr=addr.replace('ê', 'e')
                addr=addr.replace('É', 'E')
                addr=addr.replace('í', 'i')
                addr=addr.replace('ì', 'i')
                addr=addr.replace('î', 'i')
                addr=addr.replace('Í', 'I')
                addr=addr.replace('ó', 'o')
                addr=addr.replace('ò', 'o')
                addr=addr.replace('ô', 'o')
                addr=addr.replace('Ó', 'O')
                addr=addr.replace('ö', 'o')
                addr=addr.replace('Ò', 'O')
                addr=addr.replace('ú', 'u')
                addr=addr.replace('ù', 'u')
                addr=addr.replace('û', 'u')
                addr=addr.replace('Ú', 'U')
                addr=addr.replace('ü', 'u')
                addr=addr.replace('ñ', 'n')
                addr=addr.replace('Ñ', 'N')
                addr=addr.replace('Ø', 'O')
                addr=addr.replace('Ã', 'a')
                addr=addr.replace('ƒ', 'f')
                addr=addr.replace('Â', 'a')
                addr=addr.replace('¶', '-')
                addr=addr.replace('…', '-')
                addr=addr.replace('Ë', 'E')
                addr=addr.replace('†', '-')
                addr=addr.replace('ä', '-')
                addr=addr.replace('Ł', 'L')
                addr=addr.replace('ł', 'l')
                addr=addr.replace('ł', '-')
        return addr

# --------------------------------------#
# default event if no JSON file found  
# --------------------------------------#


tp = [
        {
            "name": "Cerdanya",
            "trigger": "Enter",
            "longitude": 1.863883278972198,
            "observationZone": "Line",
            "radius": 3000,
            "latitude": 42.3875017060334,
            "type": "Start"
        },
        {
            "name": "E05/Santa Cilia",
            "trigger": "Enter",
            "longitude": -0.7433333293538958,
            "observationZone": "Cylinder",
            "radius": 3000,
            "latitude": 42.569717492711,
            "type": "Turnpoint"
        },
        {
            "name": "E18/Benabarre",
            "trigger": "Enter",
            "longitude": 0.4827833303850359,
            "observationZone": "Cylinder",
            "radius": 3000,
            "latitude": 42.022216359031944,
            "type": "Turnpoint"
        },
        {
            "name": "Cerdanya",
            "trigger": "Enter",
            "longitude": 1.8638888285008988,
            "observationZone": "Cylinder",
            "radius": 3000,
            "latitude": 42.3875017060334,
            "type": "Finish"
        },
    ]

tr1={"trackId": "FLRDDE421", "pilotName": "Juanma Garete ", "competitionId": "T1", "country": "ES", "aircraft": "Duo Discus", "registration": "EC-JAA", "3dModel": "ventus2", "ribbonColors":["green"]}
tr2={"trackId": "FLRDDE1FC", "pilotName": "Sergi Pujol", "competitionId": "SP", "country": "FR", "aircraft": "Duo Discus", "registration": "D-1234", "3dModel": "ventus2", "ribbonColors":["blue"]}
tr3={"trackId": "FLRDDDB8B", "pilotName": "Luis Ferreira", "competitionId": "AA", "country": "ES", "aircraft": "Duo Discus", "registration": "EC-JAA", "3dModel": "ventus2", "ribbonColors":["green"]}
tr4={"trackId": "FLRDDBC42", "pilotName": "Santa Cilia ", "competitionId": "T1", "country": "ES", "aircraft": "Duo Discus", "registration": "EC-JAA", "3dModel": "ventus2", "ribbonColors":["green"]}
tr5={"trackId": "FLRDDC1AC", "pilotName": "Angel Casado", "competitionId": "K5", "country": "ES", "aircraft": "Janus CE", "registration": "D-2520", "3dModel": "ventus2", "ribbonColors":["red"]}
QSGP={"name": "QSGP La Cerdanya", "description": "Day 1", "taskType": "SailplaneGrandPrix", "startOpenTs": 0, "turnpoints": tp, "tracks": [tr1, tr2, tr3, tr4, tr5]}

