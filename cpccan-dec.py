#!/usr/bin/env python3
import os
import sys
import time

def date(tm):
    lt = time.localtime(tm)
    ms = int((tm%1) * 1000)
    return "%d/%d %02d:%02d:%02d.%03d" % (lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,lt.tm_sec,ms)


def field(bits,start,end):
    e=63-start
    s=63-end
    return int(bits[s:e+1],2)

def cpc_parse(msg):
    m = msg.split()
    if len(m) >= 4:
        tm = float(m[0])
        pgn = int(m[1][2:2+4],16)
        nb = m[2]
        dat = [m[3][i:i+2] for i in range(0,len(m[3]),2)]
        dat = ''.join(dat[::-1])
        bits= '{0:64b}'.format(int(dat,16))

        out = {"time":tm, "pgn":pgn, "dat":m[3]}

        if pgn == 65280:
            sysid = field(bits, 0, 1)
            axles = field(bits,16,23)
            ttms  = field(bits,24,31)
            out.update({"sysid":sysid, "axles":axles,"ttms":ttms})

        if pgn == 65281:
            sysid = field(bits, 0, 1)
            state = field(bits, 8,15)
            nottm = field(bits,33,33)
            xchg  = field(bits,35,35)
            auto  = field(bits,36,38)
            out.update({"sysid":sysid, "state":state,"nott":nottm,"xchg":xchg,"auto":auto})

        if pgn == 65282:
            sysid = field(bits, 0, 1)
            tireid= field(bits, 2, 6)
            pres  = (field(bits, 8,15)-1) * 4.706
            temp  = (field(bits,16,23)-50.0)
            state = field(bits,32,39)
            alarm = field(bits,40,47)
            batt  = field(bits,49,49)
            defect= field(bits,50,50)
            loose = field(bits,51,52)
            out.update({"sysid":sysid, "tireid":tireid,"pres":pres,"temp":temp,"state":state,"alarm":alarm,"batt":batt,"defect":defect,"loose":loose})

        if pgn == 65283:
            sysid = field(bits, 0, 1)
            out.update({"sysid":sysid})

        if pgn == 65284:
            sysid = field(bits, 0, 1)
            tireid= field(bits, 2, 6)
            gposn = field(bits, 8,15)
            locn  = field(bits,16,23)
            ttmid = field(bits,32,63)
            out.update({"sysid":sysid, "tireid":tireid,"gposn":gposn,"locn":locn,"ttmid":ttmid})
        return out

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--can',     type=str, default='can0')
parser.add_argument('-b', '--bitrate', type=int, default=1000000)
parser.add_argument('-r', '--random',  action='store_true')
parser.add_argument('-p', '--period',  type=int, default=100)
parser.add_argument('-f', '--file',    type=str, default='/dev/stdin')
parser.add_argument('-V', '--verify',  action='store_true')
parser.add_argument('-v', '--verbose', action='count', default=0)

parser.add_argument('cmd', nargs='*')
args = parser.parse_args()

fd = open(args.file)
try:
    for msg in fd:
        out = cpc_parse(msg)
        if out:
            rpt = ""
            for k,v in out.items():
                if k == 'time':
                    s = date(v)
                elif k != 'dat' or args.verbose > 0:
                    if type(v).__name__ == 'float':
                        s = " %s:%.3f" % (k,v)
                    else:
                        s = " %s:%s" % (k,str(v))
                else:
                    continue
                rpt = rpt + s
            print(rpt)
except KeyboardInterrupt:
    print("")
