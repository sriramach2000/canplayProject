#!/usr/bin/env python3
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

#parser.add_argument('cmd', nargs='*')
args = parser.parse_args()

sock= socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind((args.can,))

while True:
	try:
		msg = sock.recv(16)
	except KeyboardInterrupt:
		break

	now= time.time()
	lt = time.localtime(now)
	ms = int((now%1) * 1000)
	date = "%d/%d %02d:%02d:%02d.%03d" % (lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,lt.tm_sec,ms)

	fmt = "<IB3x8s"
	id, len, dat = struct.unpack(fmt,msg)

	print("%.6f %08x %d %s" % (now,id,len,dat.hex()), flush=True)

sock.close()
