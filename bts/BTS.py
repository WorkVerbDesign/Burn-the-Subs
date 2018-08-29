#! /usr/bin/python3 
#   Module Runner
#   This is basically burn the subs
# wonder if this should check for status ==1 first boot, use gcode maker

import settings
import sys
from threading import Thread
from time import sleep

from dataBaseClass import Sub, db
from placeAndGcode import placeNames, makeGcode
from sendGcode import gSend
from pubSubListener import ws1_start, pingTwitchServersToKeepTheConnectionAliveTask, webSocketInit
from dbUnparser import unParsify
from frontPanel import Btn_Red, Btn_Blk, LED_BB_Red, LED_BB_Grn, LED_RB_Red, LED_Grn, LED_Red, LED_RB_Grn
from ohShit import stopit

#for testing
from dbMaker import makeDb

threadQuit = False
gDone = False
streamerToggle = False


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
    print("test: added " + str(lineNo) + ' to db, done txt')
 #   while not threadQuit:
  #      entriesNo = Sub.select().where(Sub.status == burnt).count()
  #      if lineNo == entriesNo and gDone:
   #         endTheDamnTest()

def endTheDamnTest():
    global threadQuit
    
    print("main: test finished!")
    print("main: imma make a gcode text now")  
    threadQuit = True
    stopit()
    unParsify()
    db.stop()
    LED_BB_Grn.on()
    sleep(2)
    LED_BB_Grn.off()
    sys.exit()
    
def runBurner():
    global gDone
    
    while not threadQuit: 
        tomGreen = Sub.select().where(Sub.status==gcode).count()
        
        if tomGreen > 0: 
            if tomGreen >= 10:
                LED_Grn.blink()
            else:
                LED_Grn.on()
                
            if streamerToggle:
                gDone = False
                gSend()
                gDone = True
        else:
            LED_Grn.off()
        
                
def redButton():
    global streamerToggle

    LED_RB_Red.off()
    
    if streamerToggle == False:
        LED_RB_Grn.on()
        streamerToggle = True
    else:
        LED_RB_Grn.off()
        streamerToggle = False    
    
def blkButton():
    endTheDamnTest()
            
Btn_Red.when_released = redButton
Btn_Red.when_pressed = LED_RB_Red.on
Btn_Blk.when_pressed = LED_BB_Red.on
Btn_Blk.when_released = blkButton
            
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

        #virtual pubsub
        #Thread(target=testies).start()
        #Thread.daemon = True
        
        #gCodeStreamer
        runBurner()

        
    except KeyboardInterrupt:
        endTheDamnTest()
    except:
        LED_Red.on()