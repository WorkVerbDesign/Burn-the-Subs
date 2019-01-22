# Burn the subs:
# Gcode streamer! YAAAY
# I based this off:
# https://github.com/grbl/grbl/blob/master/doc/script/stream.py
# turn b's into s.write(line.encode())
# NOT THE BEES keep the \n
#

import time

import serial

from bts import settings
from bts.dataBaseClass import Sub

# settings
speed = settings.serialSpeed
serialLoc = settings.serialAddy
buffer = settings.bufferGRBL

#finally some GRBL
homeCmd = settings.homing
unitsCmd = settings.units
modeCmd = settings.dist_mode
startCmd = settings.start_cmd
feedCmd = settings.feed_rate

stopCmd = settings.stop_cmd
pulloffCmd = settings.pulloff_pos

lineCounter = []

#fixed vars
entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt

def gSend():
    # Initialize  
    s = serial.Serial(serialLoc, speed) #maybe open this in BTS main, pass it into gSend
    
    print("burning: initializing grbl...")
    s.write(b'\r\n\r\n')
    # Wait for grbl to initialize and flush startup text in serial input
    time.sleep(2)
    s.flushInput()
    
    #search db for entry, in order
    names = Sub.select().where(Sub.status == gcode)
    
    #header
    gBurn(homeCmd + unitsCmd + modeCmd + feedCmd, s)

    for name in names:
        print("burner: " + name.userName)
        gBurn(name.gCode, s, True)
        name.status = burnt
        name.save()
    
    #footer
    gBurn(stopCmd + pulloffCmd, s)
    
    print('burner: done burning!')
    s.close()
    return True

def gBurn(rawString, s, regularFlag = False): 
    lineCounter = []
    
    if regularFlag:
        firstLine = True
    else:
        firstLine = False
    
    for line in rawString.split('\n'):
        line = line.replace(' ', '')
        if len(line) > 0 and line[0] != "(":
            block = line.strip()
            lineCounter.append(len(block)+1)
            
            #debuuuug
            #print(lineCounter)
            #print(sum(lineCounter))
            
            #pump ya brakes and drive slow homie
            time.sleep(0.02)
            
            while sum(lineCounter) >= buffer - 1 or s.inWaiting() > 0:
               processRx(lineCounter, s)
                    
            s.write(block.encode() + b'\n') 
     
            #this starts the fan before the first real laser burning line
            if firstLine == True and line.find('G0') == 0:
                lineCounter.append(len(startCmd))
                s.write(startCmd.encode())
                firstLine = False
 
    #we gotta be sure the buffer completes.
    while sum(lineCounter) > 0:
       processRx(lineCounter, s)
    
def processRx(lineCounter, s):
    rxTemp = s.readline().strip()
    if rxTemp.find(b'ok') < 0 and rxTemp.find(b'error') < 0:
        print("burner:" + rxTemp.decode())
        #kill everything here
    else:
        del lineCounter[0]
        time.sleep(0.02)
        #print(lineCounter)
        #print(sum(lineCounter))

                
if __name__ == "__main__":
    gSend()