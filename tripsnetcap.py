#!/usr/bin/env python3
import signal
import sys
import string
import re
import serial
import time
import threading
import digi
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress


#5/16 17:24:44.966 &TRIPSNET;Q;z;0,1,0.4.6,95A6_0,2,0,0,0,0,0,0^000000000000;1900002546
#5/16 17:24:45.395 &TRIPSNET;M;K;0,1,0.4.6,95A6_0,2,0,0,0,0,0,0~190516172445;1900002546

#5/16 17:07:09.073 &TRIPSNET;Q;z;0,1,0.4.6,95A6_0,2,0,0,0,0,0,0^000000000000;1900002546
#5/16 17:07:09.857 &TRIPSNET;M;K;0,1,0.4.6,95A6_0,2,0,0,0,0,0,0~190516170706;1900002546

def date(tm):
    lt = time.localtime(tm)
    return "%02d%02d%02d%02d%02d%02d" % (lt.tm_year%100,lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,lt.tm_sec)

def timestamp(now):
    lt = time.localtime(now)
    ms = int((now%1) * 1000)
    return "%d/%d %02d:%02d:%02d.%03d" % (lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,lt.tm_sec,ms)

def ackmsg(msg):
    tm = time.time()
    mstr = str(msg, 'utf-8')
    if 'TRIPSNET;' in mstr:
        ack = mstr.replace('Q;S;','M;K;').replace('Q;z;','M;K;').replace('Q;E;','M;K;')
        ack = re.sub('\^.*;','~%s;'%(date(tm)),ack)
    else:
        ack = None
    return ack


#Checking command arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port',        type=str, default=None)
parser.add_argument('-b', '--baudrate',    type=int, default=57600)
parser.add_argument('-a', '--acknowledge', action='store_true')
parser.add_argument('-d', '--ackdelay',    type=float, default=0)

args = parser.parse_args()

if args.port == None:
    print("-p <serial port> required")
    print(" eg. -p /dev/ttyUSB0")
    sys.exit(1)

rf=XBeeDevice(args.port, args.baudrate)
remote = None

run = True
while run:
    rf.open()

    ack_time = None
    while True:
        try:
            pkt = rf.read_data()
        except KeyboardInterrupt:
            run = False
            print("exit")
            break
        except XBeeDevice.exception.InvalidPacketException:
            break
        if pkt:
            msg= pkt.data
            now= time.time()
            print("%s %s" %(timestamp(now), str(msg, 'utf-8')), flush=True)
            if args.acknowledge:
                if not ack_time or msg != previous:
                    ack_time = now + args.ackdelay
                    previous = msg
                if now >= ack_time:
                    ack_time = None
                    remote=pkt.remote_device
                    ack=ackmsg(msg)
                    if ack:
                        rf.send_data(remote,ack)
                        now= time.time()
                        print("%s %s" %(timestamp(now), ack), flush=True)

    rf.close()
