#!/usr/bin/python3
import os
import sys
import time
import socket
import struct

#Checking command arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--can',     type=str, default='can0')
parser.add_argument('-b', '--bitrate', type=int, default=250000)  #for CANable
parser.add_argument('-f', '--file',    type=str, default='/dev/stdin')
'''parser.add_argument('-r', '--random',  action='store_true')
parser.add_argument('-p', '--period',  type=int, default=100)
parser.add_argument('-V', '--verify',  action='store_true')
parser.add_argument('-v', '--verbose', action='count')
'''

#Opening source file
parser.add_argument('cmd', nargs='*')
args = parser.parse_args()


sock= socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind((args.can,))

basetime=None
starttime=time.time()

fd = open(args.file)
try:
    for line in fd:
        msg = line.split()
        tm,id,len,dat = float(msg[0]),int(msg[1],16),int(msg[2]),bytes.fromhex(msg[3])
        if basetime == None:
            basetime = tm
        tm -= basetime
        fmt = "<IB3x8s"
        msg = struct.pack(fmt,id,len,dat)
        now= time.time() - starttime
        sock.send(msg)

        if tm > now:
            time.sleep(tm-now)

except KeyboardInterrupt:
    print("")

sock.close()
