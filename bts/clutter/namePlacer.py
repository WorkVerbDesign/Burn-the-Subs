# places names based on database entries
#
# logarithmic scaling?
# put gcodeMaker in this, run in sequence.
# place the name, make the gcode, save it all to the db
# I don't like how this is structured, but place names will
# run the gcode maker after it saves the entry passing the
# sub object into the other function.

import settings
from PIL import Image, ImageFilter
from PIL import ImageFont, ImageDraw
from dataBaseClass import Sub, db
import random, math

#load settings!
fontFile = settings.ttfFontFile
pixMM = settings.pixelDensity
board_h = settings.boardHeightmm*pixMM  #int board width should calc in code, meh
board_l = settings.boardLengthmm*pixMM #int board height
curve = settings.fontSizeCurve
fontMax = settings.fontMaxPixHeight
fontMin = settings.fontMinPixHeight
bScale = settings.collisionPixelRadius
centerFile = settings.centerMaskPNG
failExit = settings.failsToExit

#this part is ported from the arduino fscale function
def fscale(fMin, fMax, numEntries, curve): 
    exp = -(numEntries * curve)
    unresult = math.pow(math.e, exp) * (fMax - fMin) + (fMin)
    result = int(unresult)
    
    if result > fMax:
        result = fMax
    if result < fMin:
        result = fMin
        
    return result

def placeNames():
    try:
        center = Image.open(centerFile)
    except:
        print("couldn't open center PNG")
        #sys exit, shut down threads?
    
    backing = Image.new('RGBA', (board_l,board_h), color=(255,255,255,255))
    draw = ImageDraw.Draw(backing)
    
    #overlay center keepout
    print("making virtual backing, secretly")
    center_l, center_h = center.size
    
    centerPos_l = int((board_l / 2) - (center_l / 2))
    centerPos_h = int((board_h / 2) - (center_h / 2))
    
    backing.alpha_composite(center, (centerPos_l, centerPos_h))
    
    #create backing image based on db
    nameWasPlaced = (Sub
                     .select()
                     .where(Sub.status >= 1)
                    )
    
    for placed in nameWasPlaced:
        font = ImageFont.truetype(fontFile, placed.fontSize)
        draw.text((placed.positionX,placed.positionY), placed.userName, (0,0,0), font = font)
    
    #check database for names to place
    nameToPlace = (Sub
             .select()
             .where(Sub.status == 0)
             .order_by(Sub.entryTime)
            )
    
    for sub in nameToPlace:
        totalEntries = Sub.select().where(Sub.status >= 1).count()
        
        fontSize = fscale(fontMin, fontMax, totalEntries, curve)
        
        blurRad = int(fontSize/bScale) #pixel radius of blur
        
        fail = True
        print("Placer is placing: " + sub.userName)
        
        #this should be a function for font choice based on number of existing names
        #the database population function/module/program should do this
        font = ImageFont.truetype(fontFile, fontSize)
        l,h = font.getsize(sub.userName)
        l += (blurRad * 2)
        h += (blurRad * 2)
        
        textBox = Image.new('RGBA', (l,h), color=(255,255,255,255))
        draw1 = ImageDraw.Draw(textBox)
        
        draw1.text((blurRad,blurRad), sub.userName, (0,0,0), font = font)
        
        textBox = textBox.filter(ImageFilter.GaussianBlur(radius=blurRad))
        
        while fail == True:
            #instead just do a random location for test
            board_l2 = board_l - l
            board_h2 = board_h - h
            Rboard_l = random.randint(0,board_l2)
            Rboard_h = random.randint(0,board_h2)
            fail = False
            
            #look for collision
            for i in range(0, l, 1):
                for j in range(0, h, 1):
                    shift_l = i + Rboard_l
                    shift_h = j + Rboard_h

                    r, g, b, a = backing.getpixel((shift_l, shift_h))
                    r1, g1, b1, a1 = textBox.getpixel((i, j))

                    #compare backing to text for overlap
                    if (r,g,b,a) != (255,255,255,255) and (r1,g1,b1,a1) != (255,255,255,255):
                        print(":failfish:")
                        fail = True
                        break
                if fail == True:
                    break
                 
        #now overlay that onto the board
        draw.text((Rboard_l+blurRad,Rboard_h+blurRad), sub.userName, (0,0,0), font = font)
        
        #update db with good location
        #sub.transaction(lock_type=None)
        sub.positionX = Rboard_l + blurRad
        sub.positionY = Rboard_h + blurRad
        sub.status = 1
        sub.fontSize = fontSize
        sub.save()
    
if __name__ == "__main__":
    placeNames()