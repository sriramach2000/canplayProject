# canplayProject

# cpccan-gen.py

cpccangen.py is an ECU simulator python script that generates messages to be sent to and from a CAN bus device.

In the command line this file can be run so messages can be sent to the device.

## Command

```python
./cpccan-gen.py #run script in command line from the appropriate directory
```
## How the script works
The script reads the rates from the JSON file below, and uses it to manipulate the minimum rate at which each message should be sending. Each message ID has an associated message and a rate attached to it. The rates refer to the number of times each message should come in a 1 second interval. 

```JavaScriptNotation
"60415": {
    "msg" : "9cebff33 8 0100ff63020e01c9"  ,
    "rate": 10
  },
  "65268": {
    "msg": "98fef433 8 0001c0244100009f" ,
    "rate": 2
  },
  "65280": {
    "msg": "98ff0033 8 fdff0102ff0f80c0",
    "rate": 1
```
## Open JSON File
This syntax opens the JSON file and loads the data onto the handle pgn_data
```python
with open("pgn_file.json", "r") as read_file:
    pgn_data = json.load(read_file)
```
This makes the default file to open the JSON file
```python
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('-f', '--file', type=str, default='pgn_file.json')
```
## Min-Message Rate Calculation

```python
def find_gcd(rate1,rate2):
    while(rate2):
        rate1, rate2 = rate2, rate1 % rate2
    return rate1

#divide 1000 by the rates from the json file to get the rate in milliseconds
rate_list = [1000/pgn_data['60415']['rate'], 
             1000/pgn_data['65268']['rate'], 
             1000/pgn_data['65280']['rate']] 

def min_message_rate():
    rate_1 = rate_list[0] #1st item in rate_list
    rate_2 = rate_list[1]#2nd item in rate_list 
    clock_rate = find_gcd(rate_1,rate_2)
    for i in range(1,len(rate_list)):
        clock_rate = find_gcd(clock_rate,rate_list[i])
    return clock_rate

```
## Using Message Rate for Further Calculations
In a one thousand millisecond interval there is an absolute count for the frequency of messages. And so, dividing that by the calculated clock rate gives the absolute count.   
```python
#function call of min_message_rate()
clock_rate = min_message_rate()


absolute_count = [1000/pgn_data['60415']['rate']/clock_rate , #index 0
                  1000/pgn_data['65268']['rate']/clock_rate , #index 1
                  1000/pgn_data['65280']['rate']/clock_rate ] #index 2
```
## Using the absolute count as a base counter
```python
#initialize a running count list to 0 for each element of the list
running_count = []

for element in range(len(absolute_count)):
    running_count.append(0)
```
## Decrement base by 1
Located in the main while loop of the program, this statement only holds when the running count goes back to zero. 
Therefore, the running count is decremented by one after it has been reinitialized to the absolute count. 

 
```python
if running_count[i] == 0:
    msg = genmsg2(pgn, pgn_data)
    printmsg(now, msg)
    running_count[i] = absolute_count[i]
running_count[i] -= 1
```
This for loop is also located in the main while loop. 

This looks for each element in the list and sets the pgn value to it for the respective indices. 

```python
pgn_list = ["60415","65268","65280"]
for i in range(len(absolute_count)):
    pgn = pgn_list[i]
```

## Sleep Time
For every message, this is the set number of milliseconds it will sleep before waking up to send the next message 
```python
import time
time.sleep(clock_rate/1000)
```
## How the Main Loop looks like with changes

```python
while True:

    now = time.time()
    pgn_list = ["60415", "65268", "65280"]
    pressure += 1
    if pressure > pressure_range[1]:
        pressure = pressure_range[0]
        temperature += 1
    if temperature > temperature_range[1]:
        temperature = temperature_range[0]
    try:

        # can put list name pgn_list made by Sriram instead of list of numbers
        for i in range(len(absolute_count)):
            pgn = pgn_list[i]

            # rate = pgn_data[pgn]['rate']
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
                    printmsg(now,msg)
                    running_count[i] = absolute_count[i]
                running_count[i] -= 1
                time.sleep(clock_rate/1000)


    

    except KeyboardInterrupt:
        print("")
        break
```
