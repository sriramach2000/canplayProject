#!/usr/bin/env python3
import os
import sys
import time


def field(bits, start, end):
    e = 63 - start
    s = 63 - end
    return int(bits[s:e + 1], 2)


# initialized to the value None so there is no issue when calling them in consecutive statements in the function
def genmsg(pgn, tireid=None, temperature=None, pressure=None, tirepos=None):
    if pgn == 60415:
        msg = "9cebff33 8 0100ff63020e01c9"

    if pgn == 65268:
        msg = "98fef433 8 0001c0244100009f"

    if pgn == 65280:
        msg = "98ff0033 8 fdff0102ff0f80c0"

    if pgn == 65281:
        msg = "98ff0133 8 fd01feff41c0ff3f"

    if pgn == 65282:
        msg = "98ff0233 8 iippttfd0802e0ff"
        msg = msg.replace('ii', "%02x" % (tireid * 4 + 0x81))

        msg = msg.replace('tt', "%02x" % (int(temperature + 50.0)))

    if pgn == 65283:
        msg = ""

    if pgn == 65284:
        msg = "98ff0433 8 iippll0205d3946c"
        msg = msg.replace('ii', "%02x" % (tireid * 4 + 0x81))
        msg = msg.replace('pp', "%02x" % (tirepos))
        msg = msg.replace('ll', "%02x" % (tireid))

    if pgn == 65286:
        msg = "98ff0633 8 fd0500129cf0ffff"

    if pgn == 65290:
        msg = "98ff0a33 8 01aeadae000000ff"

    if pgn == 60671:
        msg = "9cecff33 8 20160004ffcafe00"
    return msg

import json
with open("pgn_file.json", "r") as read_file:
    pgn_data = json.load(read_file)

def genmsg2(pgn, pgn_data,tireid=None, temperature=None, pressure=None, tirepos=None):

    msg = ''
    if pgn in pgn_data:
        msg = pgn_data[pgn]['msg']

        if pgn == 65282:
            msg = pgn_data['65282']['msg']
            msg = msg.replace('ii', "%02x" % (tireid * 4 + 0x81))

            msg = msg.replace('tt', "%02x" % (int(temperature + 50.0)))

        if pgn == 65284:
            msg = pgn_data['65284']['msg']
            msg = msg.replace('ii', "%02x" % (tireid * 4 + 0x81))
            msg = msg.replace('pp', "%02x" % (tirepos))
            msg = msg.replace('ll', "%02x" % (tireid))

    return msg



def printmsg(now, msg):
    print("%.6f %s" % (now, msg), flush= True)



import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, default='pgn_file.json')

args = parser.parse_args()


def find_gcd(rate1,rate2):
    while(rate2):
        rate1, rate2 = rate2, rate1 % rate2
    return rate1

def pseudo_min_message_rate(pgn_data):

    clock_frequency = 1.0

    for k,v in pgn_data.items():
        clock_frequency *= v['rate']
    return clock_frequency

rate_list = []
for k,v in pgn_data.items():
    rate = v['rate']

    rate = 1000/rate

    rate_list.append(rate)




def min_message_period():

    rate_1 = int(rate_list[0])
    rate_2 = int(rate_list[1])
    clock_rate = find_gcd(rate_1,rate_2)
    for i in range(2,len(rate_list)):
        clock_rate = find_gcd(clock_rate,rate_list[i])


#   converted to milliseconds in time.sleep function in main loop
    return clock_rate
clock_rate = min_message_period()

absolute_count = []

for k, v in pgn_data.items():
    absolute_count.append(int((1000/ v['rate'])/clock_rate))


running_count = []
for element in range(len(absolute_count)):
    running_count.append(0)



pressure_range = [800, 900]
temperature_range = [0, 100]

pressure = pressure_range[0]
temperature = temperature_range[0]

pgn_list = []

for k, v in pgn_data.items():
    list= pgn_list.append(v['ID'])


start = time.time()

while True:

    now = time.time()
   # pgn_list = ["60415", "65268", "65280"]
    pressure += 1
    if pressure > pressure_range[1]:
        pressure = pressure_range[0]
        temperature += 1
    if temperature > temperature_range[1]:
        temperature = temperature_range[0]
    try:

        for i in range(len(absolute_count)):
            pgn = pgn_list[i]

            if pgn == 65284:

                msg = genmsg2(pgn, pgn_data, tireid=0, tirepos=0xc3)
                printmsg(now, msg)
                msg = genmsg2(pgn, pgn_data, tireid=1, tirepos=0xcb)
                printmsg(now, msg)
                msg = genmsg2(pgn, pgn_data, tireid=2, tirepos=0xd3)
                printmsg(now, msg)
                msg = genmsg2(pgn, pgn_data, tireid=3, tirepos=0xdb)
            elif pgn == 65282:
                p = pressure
                # if (int(count/10)) % 10 == 0:
                #    p = 0
                msg = genmsg2(pgn, pgn_data, tireid=0, pressure=p, temperature=temperature)
                printmsg(now, msg)
                msg = genmsg2(pgn, pgn_data, tireid=1, pressure=p + 1, temperature=temperature + 1)
                printmsg(now, msg)
                msg = genmsg2(pgn, pgn_data, tireid=2, pressure=p + 2, temperature=temperature + 2)
                printmsg(now, msg)
                msg = genmsg2(pgn, pgn_data, tireid=3, pressure=p + 3, temperature=temperature + 3)
            else:
                if running_count[i] == 0:
                    msg = genmsg2(pgn, pgn_data)
                    #FOR TESTING PURPOSES ONLY
                 #   print(i+1)
                 # below is actual message

                    printmsg(now,msg)
                    running_count[i] = absolute_count[i]

                elif running_count[i] <= 1:
                    msg = genmsg2(pgn, pgn_data)
                    # FOR TESTING PURPOSES ONLY
                #    print(i+1)
                    # below is actual message
                    printmsg(now,msg)
                    running_count[i] = absolute_count[i]
                running_count[i] -= 1
                time.sleep(clock_rate/1000)



    #the rate is in messages per second. so if the rate is 10, it is 1 msg every 100 ms

    except KeyboardInterrupt:
        print("")
        break