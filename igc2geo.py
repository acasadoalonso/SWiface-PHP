#!/usr/bin/python3

#
# Convert an .IGC file to a .JSON file
#


import sys, os
from datetime import date, timedelta
from copy import deepcopy
from collections import OrderedDict

DefaultExt = ".json"
CoordinatePrec = 6

def mintodeg(degmin):
    deg = int(float(degmin)/100)
    return round(deg + (float(degmin) - deg*100)/60.0, CoordinatePrec)

def igctodate(arg):
    # IGC FR Spec w AL4A, A2.4
    utcday = int(arg[0:2])
    utcmonth = int(arg[2:4])
    utcyear = int(arg[4:6])
    # No specification for low end of 19xx dates, choice of 1990 arbitrary
    utcyear += utcyear >= 90 and 1900 or 2000
    return "%04d-%02d-%02d" % (utcyear, utcmonth, utcday)

def igctotime(arg, tds=None):
    # IGC FR Spec w AL4A, A2.4
    hour = int(arg[0:2])
    minute = int(arg[2:4])
    second = int(arg[4:6])
    hms = "%02d:%02d:%02d" % (hour, minute, second)
    if tds:
        int(tds) # Make sure valid int
        hms += "." + tds
    return hms

def igctolat(arg, lad=None):
    degree = int(arg[0:2])
    minute = int(arg[2:4])
    minutedecimal = int(arg[4:7])
    direction = arg[7:8].upper() == 'N' and '+' or '-'
    lat = "%s%02d%02d.%03d" % (direction, degree, minute, minutedecimal)
    if lad:
        int(lad) # Make sure valid int
        lat += lad
    return mintodeg(lat)

def igctolon(arg, lod=None):
    degree = int(arg[0:3])
    minute = int(arg[3:5])
    minutedecimal = int(arg[5:8])
    direction = arg[8:9].upper() == 'E' and '+' or '-'
    lon = "%s%03d%02d.%03d" % (direction, degree, minute, minutedecimal)
    if lod:
        int(lod) # Make sure valid int
        lon += lod
    return mintodeg(lon)

def A(parser, line):
    if len(line) >= 7:
        parser.setattr("features/flight/properties/device/ManufacturerID", line[1:4])
        parser.setattr("features/flight/properties/device/SerialNumber", line[4:7])
        if len(line) > 7:
            parser.setattr("features/flight/properties/device/DeviceData", line[7:])
    else:
        parser.note("Invalid A record")

def HFDTE(parser, arg):
    args = arg.split(',')
    date = igctodate(args[0])
    if date:
        parser.date = date
        #parser.setattr("features/flight/properties/DateUTC", date)
        if len(args) > 1:
            parser.setattr("features/flight/properties/declaration/FlightNum", int(args[1].strip()))
    else:
        parser.note("Invalid HFDTE record")
        return None

def HFPLT(parser, arg):
    parser.setattr('features/flight/properties/declaration/PilotInCharge', arg)

def HFCM2(parser, arg):
    parser.setattr('features/flight/properties/declaration/Crew', [arg])

def HFGTY(parser, arg):
    parser.setattr('features/flight/properties/declaration/AircraftType', arg)

def HFGID(parser, arg):
    parser.setattr('features/flight/properties/declaration/AircraftID', arg)

def HFDTM(parser, arg):
    parser.setattr('features/flight/properties/device/GNSS/Datum', arg)

def HFRFW(parser, arg):
    parser.setattr('features/flight/properties/device/FirmwareVersion', arg)

def HFRHW(parser, arg):
    parser.setattr('features/flight/properties/device/HardwareVersion', arg)

def HFFTY(parser, arg):
    args = arg.split(',')
    nargs = len(args)
    if nargs:
        if nargs == 1:
            parser.note("HFFTY missing manufacturer name field, FR Spec 2 AL5, A3.2.5, A7")
            manufacturer = "unknown"
            model = args[0].strip()
        elif nargs > 1:
            manufacturer = args[0].strip()
            model = args[1].strip()
        parser.setattr("features/flight/properties/device/Manufacturer", manufacturer)
        parser.setattr("features/flight/properties/device/Model", model)
    else:
        parser.note("Invalid HFFTY record FR Spec 2 AL5, A3.2.5, A7")

def HFGPS(parser, arg):
    args = arg.split(',')
    nargs = len(args)
    if nargs >= 1:
        data = { 'Manufacturer': args[0] }
        if nargs < 2:
            parser.note("HFGPS missing required fields model, channels, max altitude, FR Spec 2 AL5, A3.2.5")
        else:
            data['Model'] = args[1]
            if nargs < 3:
                parser.note("HFGPS missing required fields channels, max altitude, FR Spec 2 AL5, A3.2.5")
            else:
                try:
                    data['Channels'] = int(args[2])
                except ValueError:
                    parser.note("HFGPS invalid channel field, FR Spec 2 AL5, A3.2.5")
                if nargs < 4:
                    parser.note("HFGPS missing required field max altitude, FR Spec 2 AL5, A3.2.5")
                else:
                    try:
                        data['AltitudeMax'] = int(args[3])
                    except ValueError:
                        parser.note("HFGPS maximum altitude format invalid, FR Spec 2 AL5, A3.2.5")
                    if nargs > 4:
                        data['Systems'] = args[4:]
                    else:
                        data['Systems'] = ['GPS']
        parser.setattr("features/flight/properties/device/GNSS", data)
        return None
    parser.note("Invalid HFGPS record FR Spec 2 AL5, A3.2.5")
    return None

def HFPRS(parser, arg):
    args = arg.split(',')
    nargs = len(args)
    if nargs >= 1:
        data = { 'Manufacturer': args[0] }
        if nargs < 2:
            parser.note("HFPRS missing required fields sensor type, max altitude, FR Spec 2 AL5, A3.2.5")
        else:
            data['Model'] = args[1]
            if nargs < 3:
                parser.note("HFPRS missing required field max altitude, FR Spec 2 AL5, A3.2.5")
            else:
                try:
                    data['AltitudeMax'] = int(args[2].strip())
                except ValueError:
                    parser.note("Invalid HFPRS maximum pressure altitude FR Spec 2 AL5, A3.2.5")
        parser.setattr("features/flight/properties/device/PressureSensor", data)
    else:
        parser.note("Invalid HFPRS record FR Spec 2 AL5, A3.2.5")
    return None

def HFFRS(parser, arg):
    parser.setattr('features/flight/properties/SecuritySuspect', arg)

def HFMOP(parser, arg):
    args = arg.split(',')
    nargs = len(args)
    if nargs >= 1:
        data = OrderedDict(Manufacturer=args[0])
        if nargs < 2:
            parser.note("HFMOP missing required fields MOP state, MOP type, MOP model, FR Spec 2 AL5, A3.2.5")
        else:
            data['State'] = args[1]
            if nargs < 3:
                parser.note("HFMOP missing required fields MOP type, MOP model, FR Spec 2 AL5, A3.2.5")
            else:
                data['Type'] = args[2]
                if nargs < 4:
                    parser.note("HFMOP missing required field MOP model, FR Spec 2 AL5, A3.2.5")
                else:
                    data['Model'] = args[3]
        parser.setattr("features/flight/properties/device/MOP", data)
    else:
        parser.note("Invalid HFMOP record format, FR Spec 2 AL5, A3.2.5")

def HFCCL(parser, arg):
    parser.setattr('features/flight/properties/declaration/CompetitionClass', arg)

def HFCID(parser, arg):
    parser.setattr('features/flight/properties/declaration/CompetitionID', arg)

def HOSOF(parser, arg):
    parser.note("Non-IGC header, FR Spec 2 AL5, A3.2.7.5")

def HOFSP(parser, arg):
    parser.note("Non-IGC header, FR Spec 2 AL5, A3.2.7.5")

def HFFSP(parser, arg):
    parser.note("Non-IGC header, FR Spec 2 AL5, A3.2.7.5")

def HFALG(parser, arg):
    parser.note("Non-IGC header, FR Spec 2 AL5, A3.2.7.5")

def HFALP(parser, arg):
    parser.note("Non-IGC header, FR Spec 2 AL5, A3.2.7.5")

def HFFXA(parser, arg):
    parser.note("Obsolete IGC header, FR Spec 2 AL5, A3.2.7.5")

headerRecords = {
    'HFDTE': HFDTE,
    'HFPLT': HFPLT,
    'HFCM2': HFCM2,
    'HFGTY': HFGTY,
    'HFGID': HFGID,
    'HFDTM': HFDTM,
    'HFRFW': HFRFW,
    'HFRHW': HFRHW,
    'HFFTY': HFFTY,
    'HFGPS': HFGPS,
    'HFPRS': HFPRS,
    'HFFRS': HFFRS,
    'HFMOP': HFMOP, # Optional
    'HFCCL': HFCCL, # Optional
    'HFCID': HFCID, # Optional
    'HOSOF': HOSOF, # Non-IGC
    'HOFSP': HFFSP, # Non-IGC
    'HFFSP': HFFSP, # Non-IGC
    'HFALG:': HFALG, # Non-IGC
    'HFALP:': HFALP, # Non-IGC
    'HFFXA': HFFXA # Obsolete
}

requiredHeaderRecords = set((
    'HFDTE', 'HFPLT', 'HFCM2', 'HFGTY', 'HFGID',
    'HFDTM', 'HFRFW', 'HFRHW','HFFTY', 'HFGPS', 'HFPRS'
))

mandatoryRecords = set([
    'A', 'H', 'I', 'B', 'F', 'G'
])

def H(parser, line):
    subtype = line[0:5].upper()
    if len(line) >= 5 and subtype in headerRecords:
        parser.recordsSeen.add(subtype)
        arg = line[5:].split(':')[-1].lstrip()
        headerRecords[subtype](parser, arg)
    else:
        parser.note("Invalid H record format, FR Spec, 2 w AL5, A3.2")

def I(parser, line) :
    for addition in parser.parseAdditions():
        tlc = addition['TLC']
        parser.appendattr("features/flight/properties/fixColumns", tlc)
        parser.addToBRec(addition)

def J(parser, line) :
    for addition in parser.parseAdditions():
        parser.addToKRec(addition)

def C(parser, line):
    try:
        if 'C' not in parser.recordsSeen:
            # C line 1:
            taskdate = igctodate(line[1:7])
            tasktime = igctotime(line[7:13])
            flightdate = line[13:19] # Obsolete
            tasknumber = line[19:23] # Obsolete
            numturnpoints = int(line[23:25])
            taskname = line[25:].strip()
            if taskname:
                parser.setattr('features/flight/properties/declaration/Task', taskname)
            parser.setattr('features/flight/properties/declaration/PointCount', numturnpoints)
            parser.setattr('features/flight/properties/declaration/Timestamp', '%sT%sZ'% (taskdate, tasktime))
        else:
            # Other C lines
            lat = igctolat(line[1:9])
            lon = igctolon(line[9:18])
            name = line[18:]
            geometry = (lat and lon) and dict(type='Point', coordinates=[ lon, lat ]) or None
            feature = OrderedDict(id=parser.pointID(name), type='Feature', properties=OrderedDict(ID=name), geometry=geometry)
            parser.appendattr("features", feature)

    except ValueError:
        parser.note("Invalid C record format, FR Spec 2 AL5, A3.5")

def L(parser, line):
    try:
        time = parser.timestamp()
        source = line[1:4].strip()
        text = line[4:].strip()
        parser.log(time, source, text)
    except ValueError:
        parser.note("Invalid L record FR Spec 2 AL5, A4.5")

def D(parser, line):
    if len(line) >= 6:
        qualifier = line[1:2] == '1' and 'OFF' or line[1:2] == '2' and 'ON'
        station = line[2:6].strip()
        if qualifier:
            timestamp = parser.timestamp()
            text = qualifier + (station and ':' + station or '')
            parser.event(timestamp, "DGNSS", text)
            return
    parser.note("Invalid D Record, FR Spec 2 AL5, A4.6")

def F(parser, line):
    try:
        time = igctotime(line[1:7])
        sats = [ line[c:c+2] for c in range(7, len(line) - 1, 2) ]
        if sats and time:
            timestamp = parser.timestamp(time)
            parser.event(timestamp, "SATS", sats)
            return
    except ValueError:
        parser.note("Invalid F record FR Spec 2 AL5, A4.3")

def B(parser, line):
    try:
        if len(line) >= 34:
            time = igctotime(line[1:7], parser.getBAddition('TDS'))
            timestamp = parser.timestamp(time)
            lat = igctolat(line[7:15], parser.getBAddition('LAD'))
            lon = igctolon(line[15:24], parser.getBAddition('LOD'))
            validity = line[24:25]
            pressalt = int(line[25:30])
            gnssalt = int(line[30:35])
            data = [timestamp, pressalt]
            data.extend(parser.getBAdditions())
            parser.fix(lat, lon, gnssalt, data)
    except ValueError:
        parser.note("Invalid B record FR Spec 2 AL5, A4.1")

def E(parser, line):
    try:
        if len(line) >= 10:
            time = igctotime(line[1:7])
            code = line[7:10].strip()
            if time and code:
                timestamp = parser.timestamp(time)
                text = line[10:].strip()
                parser.event(timestamp, code, text)
                return
    except ValueError:
        pass
    parser.note("Invalid E Record, FR Spec 2 AL5, A4.2")

def K(parser, line):
    try:
        if len(line) >= 7:
            time = igctotime(line[1:7], parser.getKAddition('TDS'))
            timestamp = parser.timestamp(time)
            data = parser.getKAdditions()
            parser.event(timestamp, "REC", data)
            return
    except ValueError:
        pass
    parser.note("Invalid K Record, FR Spec 2 AL5, A4.4")

def G(parser, line):
    if not parser.findobj("features", "signatures"):
        parser.appendattr("features", 
            OrderedDict(
                id = "signatures", 
                type = "Feature", 
                properties = OrderedDict( IGC=[] ),
                geometry = None ))
    parser.appendattr("features/signatures/properties/IGC", line[1:])

recordOrder = [
    { 'A': A },
    { 'H': H },
    { 'I': I, 'J': J },
    { 'L': L, 'C': C },
    { 'L': L, 'D': D },
    { 'L': L, 'F': F, 'B': B, 'E': E, 'K': K },
    { 'G': G },
]

tlcExtensions = {
    'FXA': { 'name': 'FixAccuracy', 'type': int },
    'SIU': { 'name': 'SatellitesInUse', 'type': int },
    'ENL': { 'name': 'EngineNoiseLevel', 'type': int }
}

def tlctoname(tlc):
    extension = tlcExtensions.get(tlc)
    return extension and extension.get('name') or tlc

def tlctotype(tlc):
    extension = tlcExtensions.get(tlc)
    return extension and extension.get('type') or str

class IGCparser(object):
    shownotes = True
    def __init__(self):
        self.clear()

    def clear(self):
        self.file = None
        self.filename = "unknown.igc"
        self.lineno = 0
        self.line = None
        self.BRecAdditions = OrderedDict()
        self.KRecAdditions = OrderedDict()
        self.recordsSeen = set()
        self.root = OrderedDict()
        self.date = None
        self.time = "00:00:00"
        self.pointNum = 1

    def timestamp(self, time=None):
        # What about midnight?
        if time and self.time and time[:2] == '00' and self.time[:2] == '23':
            # Uh-oh, midnight happened
            self.date = (date.fromisoformat(self.date) + timedelta(days=1)).isoformat()
        self.time = time or self.time
        return '%sT%sZ' % (self.date, self.time)

    def makeobj(self, *path):
        obj = self.root
        for key in path:
            if issubclass(dict, obj.__class__) or issubclass(OrderedDict, obj.__class__):
                obj = obj.setdefault(key, OrderedDict())
            elif issubclass(list, obj.__class__):
                #node = next((o for o in obj if o.get('id') == key), None)
                node = None
                for o in obj:
                    if o.get('id') == key:
                        node = o
                        break
                if not node:
                    node = { "id": key }
                    obj.append(node)
                obj = node                
        return obj

    def findobj(self, *path):
        obj = self.root
        for key in path:
            if issubclass(dict, obj.__class__) or issubclass(OrderedDict, obj.__class__):
                if key in obj:
                    obj = obj[key]
                else:
                    return None
            elif issubclass(list, obj.__class__):
                node = next((o for o in obj if o.get('id') == key), None)
                if node:
                    obj = node
                else:
                    return None
            else:
                raise KeyError("%r not in path %r" % (key, path))
        return obj
    
    def getattr(self, path, value):
        path = path.split('/')
        if path:
            try:
                return self.findobj(*path)
            except KeyError:
                pass

    def setattr(self, path, value):
        path = path.split('/')
        if path:
            parent = self.makeobj(*path[:-1])
            parent[path[-1]] = value

    def appendattr(self, path, value):
        path = path.split('/')
        if path:
            parent = self.makeobj(*path[:-1])
            parent.setdefault(path[-1], []).append(value)

    def note(self, msg):
        if self.shownotes:
            if self.line:
                print("> %s[%d] %s:\n%s" % (self.filename, self.lineno, msg, self.line), file=sys.stderr)
            else:
                print("> %s[%d] %s" % (self.filename, self.lineno, msg), file=sys.stderr)

    def open(self, filename):
        self.file = open(filename, 'r')
        self.filename = self.file.name
        self.lineno = 0;

    def close(self):
        self.file.close()
        self.file = None

    def readline(self):
        self.line = self.file.readline()
        if self.line:
            self.line = self.line.rstrip()
            self.lineno += 1
        else:
            self.line = None
        return self.line

    def readlines(self):
        while self.readline() != None:
            yield self.line

    def addToBRec(self, addition):
        self.BRecAdditions[addition['TLC']] = addition

    def addToKRec(self, addition):
        self.KRecAdditions[addition['TLC']] = addition

    def parseAdditions(self):
        line = self.line
        try:
            n = int(line[1:3])
            for i in range(n):
                c = 3 + i*7
                start = int(line[c:c+2])
                finish = int(line[c+2:c+4])
                tlc = line[c+4:c+7]
                yield { 'Start': start - 1, 'Finish': finish, 'TLC': tlc }
        except ValueError:
            self.note("Invalid %s Record" % line[0:1])

    def getAddition(self, additions, tlc):
        try:
            addition = additions[tlc]
            return tlctotype(tlc)(self.line[addition['Start']:addition['Finish']])
        except KeyError:
            pass

    def getBAddition(self, tlc):
        return self.getAddition(self.BRecAdditions, tlc)

    def getKAddition(self, tlc):
        return self.getAddition(self.KRecAdditions, tlc)

    def getAdditions(self, additions):
        return [ self.getAddition(additions, tlc) for tlc in additions ]

    def getBAdditions(self):
        return self.getAdditions(self.BRecAdditions)

    def getKAdditions(self):
        return self.getAdditions(self.KRecAdditions)

    def pointID(self, name):
        if name == "TAKEOFF":
            return "takeoff"
        elif name == "LANDING":
            return "landing"
        else:
            pointID = "point%03d" % self.pointNum
            self.pointNum += 1
            return pointID

    def fix(self, lat, lon, alt, data):
        self.appendattr("features/flight/geometry/coordinates", 
                            [ lon, lat, round(alt, 1) ])
        self.appendattr("features/flight/properties/fixes", data)

    def event(self, timestamp, code, data=None):
        event = [ timestamp, code, data ]
        self.appendattr("features/flight/properties/events", event)

    def log(self, timestamp, source, data=None):
        entry = [ timestamp, source, data ]
        self.appendattr("features/log/properties/entries", entry)

    def parse(self, file=None):
        self.clear()
        if file:
            self.file = file
            self.filename = file.name or "unknown.igc"
            self.setattr('type', 'FeatureCollection')
            self.setattr('features', [
                # Put log first, for now, it's ulitmately the last feature
                OrderedDict(id="log",
                    type = "Feature",
                    properties = OrderedDict(
                        entries=[]
                    )
                ),
                OrderedDict(id="flight", 
                    type="Feature", 
                    properties = OrderedDict(
                        device = OrderedDict(
                            ManufacturerID = None,
                            SerialNumber = None,
                            Manufacturer = None,
                            Model = None,
                            FirmwareVersion = None,
                            HardwareVersion = None
                        ),
                        declaration = OrderedDict(),
                        dataColumns = [],
                        fixColumns = ['UTC', 'PRS'], 
                        fixes = [],
                        events = [] ), 
                    geometry=OrderedDict(type="LineString", coordinates=[])
                )
            ])
            current = 0
            for line in self.readlines():
                if line:
                    rectype = line[0].upper()
                    c = current
                    while c < len(recordOrder) and rectype not in recordOrder[c]:
                        c += 1
                    if c >= len(recordOrder):
                        self.note("Unrecognized record")
                    else:
                        current = c
                        result = recordOrder[current][rectype](self, line)
                        self.recordsSeen.add(rectype)
            # Pop log and add last
            features = self.findobj("features")
            log = features.pop(0)
            features.append(log)
            if not mandatoryRecords.issubset(self.recordsSeen):
                self.note("Missing mandatory record(s) %s, FR Spec 2 AL5, A2.5.7" % ', '.join(list(mandatoryRecords.difference(self.recordsSeen))))
            if not requiredHeaderRecords.issubset(self.recordsSeen):
                self.note("Missing required H record(s) %s, FR Spec 2 AL5, A3.2.4" % ', '.join(list(requiredHeaderRecords.difference(self.recordsSeen))))
            return self.root

import json

def igc2geo(file):
    return IGCparser().parse(file)

def main(*args):
    if not args:
        print("usage: igc2geo input.igc [ output.json ]", file=sys.stderr)
    else:
        src = args[0]
        if len(args) > 1:
            dst = argv[1]
        else:
            name, ext = os.path.splitext(src)
            dst = name + DefaultExt
        try:
            with open(src, 'r') as input:
                res = igc2geo(input)
                with open(dst, 'w') as output:
                    json.dump(res, output, sort_keys=False, indent=2, separators=(',', ': '))
        except Exception as e:
            print(e.__class__.__name__ + ': ' + str(e), file=sys.stderr)

if __name__ == '__main__':
    main(*sys.argv[1:])
