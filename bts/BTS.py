#   Module Runner
#   This is basically burn the subs
# wonder if this should check for status ==1 first boot, use gcode maker

import settings
import sys
from threading import Thread

from dataBaseClass import Sub, db
from placeAndGcode import placeNames, makeGcode
from sendGcode import gSend
from pubSubListener import ws1_start, pingTwitchServersToKeepTheConnectionAliveTask, webSocketInit
from dbUnparser import unParsify

#for testing
#from dbMaker import makeDb

threadQuit = False
gDone = False

entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt

def runPlace():
    while not threadQuit:
        noNotPlaced = Sub.select().where(Sub.status==entered).count()
        
        if noNotPlaced > 0:
            placeNames()


def deraLict():
    noNotGd = Sub.select().where(Sub.status==placed).count()
        
    if noNotGd > 0:
        print("main: found un-gcoded stuff, fixing")
        gList = Sub.select().where(Sub.status==placed)
        for name in gList:
            makeGcode(name)
            
def testies():
    global gDone
    lineNo = makeDb()
    while not threadQuit:
        entriesNo = Sub.select().where(Sub.status == burnt).count()
        if lineNo == entriesNo and gDone:
            endTheDamnTest()

def endTheDamnTest():
    global threadQuit
    
    print("main: test finished!")
    print("main: imma make a gcode text now")  
    threadQuit = True
    unParsify()
    db.stop()
    sys.exit()
    
def runBurner():
    global gDone
    
    while not threadQuit:
        tomGreen = Sub.select().where(Sub.status==gcode).count()
        if tomGreen > 0:
            gDone = False
            gSend()
            gDone = True
            
if __name__ == "__main__":
    print("Burn the Subs started")
    try:  
        #check if there are derelict entries
        deraLict()
        
        #pubSub
        webSocketInit()
        
        #placer
        Thread(target=runPlace).start()
        Thread.daemon = True

        #gCodeStreamer
        runBurner()
        
        #virtual pubsub
        #testies()
        
    except KeyboardInterrupt:
        endTheDamnTest()