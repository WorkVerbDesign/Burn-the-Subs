#! /usr/bin/python3 
#   Module Runner
#   This is basically burn the subs
# wonder if this should check for status ==1 first boot, use gcode maker

import sys
from threading import Thread

from . import settings
from .dataBaseClass import Sub, db
from .dbMaker import makeDb
from .makePng import makeOnePng
from .placeNoGcode import placeNames

threadQuit = False

entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt

def runPlace():
    while not threadQuit:
        noNotPlaced = Sub.select().where(Sub.status==entered).count()
        
        if noNotPlaced > 0:
            placeNames()
            
def testies(testicalNum):
    lineNo = makeDb()+testicalNum
    print("test: added " + str(lineNo) + ' to db, done txt')
    while not threadQuit:
        entriesNo = Sub.select().where(Sub.status >= placed).count()
        if lineNo == entriesNo:
            endTheDamnTest()
   
   
def endTheDamnTest():
    global threadQuit
    
    print("main: trying to exit clean!")
    threadQuit = True
    #stopit()
    #unParsify()
    makeOnePng()
    db.stop()
   # LED_BB_Grn.on()
    #sleep(2)
    #LED_BB_Grn.off()
    sys.exit() 
    
if __name__ == "__main__":
    print("main: Octo special Burn the Subs started")
    try:  
        #check if there are derelict entries
        #deraLict()
        
        #pubSub
        #webSocketInit()
        
        #placer
        #runPlace()
        Thread(target=runPlace).start()
        Thread.daemon = True

        #virtual pubsub
        chromazomes = Sub.select().where(Sub.status >= placed).count()
        testies(chromazomes)
        #Thread(target=testies).start()
        #Thread.daemon = True
        
        #gCodeStreamer
        #runBurner()
    except KeyboardInterrupt:
        endTheDamnTest()