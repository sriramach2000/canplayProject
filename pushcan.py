#!/usr/bin/python3

import os
import sys
import serial
import time
import logging
import can

#CANSTART = 0x18ff0633
CANSTART = 0x1cebff33
CANPULL  = 0x2d7
CANXFR   = 0x2d8
CANDONE  = 0x2d9
CANXRES  = 0x2da

#Checking command arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--can',     type=str, default='can0')
parser.add_argument('-b', '--bitrate', type=int, default=250000)  #for CANable
parser.add_argument('-i', '--infile',  type=str, default="PushCan.txt")
parser.add_argument('-o', '--otfile',  type=str, default="CanOtTmStmpd.txt")
'''parser.add_argument('-r', '--random',  action='store_true')
parser.add_argument('-p', '--period',  type=int, default=100)
parser.add_argument('-V', '--verify',  action='store_true')
parser.add_argument('-v', '--verbose', action='count')
'''

#Opening source file
parser.add_argument('cmd', nargs='*')
args = parser.parse_args()
CanInFilePathName="/home/cjanand1954/dev/trucklite/"+args.infile
CanFile = open(CanInFilePathName, "r")
#opening CAN out time stamped log file
CanOutFilePathName="/home/cjanand1954/dev/trucklite/"+args.otfile
CanTmStmpdFile = open(CanOutFilePathName, "a")


#Setting up CANable USB CAN adapter
checkcan0=os.popen("ifconfig -a | grep -i can").read()
CANableACM=os.popen("ls /dev/ttyA*").read()
UseACM= CANableACM[:-1]
if not checkcan0:
	print("CANable set up as can0 at ", CANableACM, "\n")
	setupcan0 = "sudo slcand -o -s5 " + UseACM + " can0"
	#print(setupcan0)
	os.system(setupcan0)
	os.system("sudo ifconfig can0 up")
else :
	print("CANable already set up as " + checkcan0[:4] + UseACM +"\n")


#Setting up socket for CAN ACMx
bus = can.interface.Bus(bustype='socketcan',channel=args.can,bitrate=args.bitrate)
'''
canstring=str(bus.recv())
canstringOld='0'
#Streaming CAN to fileS
while True:
	if canstringOld!=canstring:
		print(canstring)
		CanFile.write(canstring+"\n")
		canstringOld=canstring
		canstring=str(bus.recv())
'''

'''
count=0
while count<11:
	count=count+1
	canmsg=can.Message(data=databytes, arbitration_id=CANSTART, extended_id=True)
#	print("Message to be sent: \n", canmsg)
	bus.send(canmsg)
#	canstring=str(bus.recv())
#	print(str(count) +":"+str(canstring))
'''

#Reading input file line by line
nuMsgFrmFile = CanFile.readline()
nuMsgTime=nuMsgFrmFile[11:28]
nuCanID=nuMsgFrmFile[36:44]
nuCanDataLen=nuMsgFrmFile[71]
x=nuMsgFrmFile[76:99]
nuCanData=bytearray()
while nuMsgFrmFile!="":
	print(nuMsgFrmFile, nuMsgTime)
	for n in range (0,21,3):
		nuCanData.append(int((x[n]+x[n+1]),16))		#create byte array from string	
		#	nuCanData=[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
	canmsg=can.Message(data=nuCanData, arbitration_id=int(nuCanID,16), extended_id=True)
	canSendOk=bus.send(canmsg)
	#	CanMsgSndTime=str(time.time()).zfill(20)
	CanMsgSndTime=time.time()
	CanTmStmpdFile.write(str(round(CanMsgSndTime,6))+'\t '+ nuMsgFrmFile)
	oldMsgFrmFile=nuMsgFrmFile
	oldMsgTime=nuMsgTime
	nuMsgFrmFile = CanFile.readline()
	if nuMsgFrmFile != '':	              
		nuMsgTime=nuMsgFrmFile[11:28]
		nuCanID=nuMsgFrmFile[36:44]
		nuCanDataLen=nuMsgFrmFile[71]
		x=nuMsgFrmFile[76:99]
		nuCanData=bytearray()
		time.sleep(((float(nuMsgTime[1:-1]) - float(oldMsgTime[1:-1])))/1)   #div by 2 to go twice as fast 
	else:
		break

CanFile.close()
CanTmStmpdFile.close()
