#combines the previous name Placer and gCode maker
#uses setting file, PIL, cueXXIII's gcode parser
#peewee in squliteQueue  mode. Just... everything.
#the placer takes too long to run on larger names
#due to pixel compare. F. So making gcode after placement.

import math
import random
import re

from PIL import Image, ImageFilter
from PIL import ImageFont, ImageDraw

from . import settings
from .dataBaseClass import Sub
from .gCodeParser import GParseQuick

#from frontPanel import LED_TYel, LED_BYel

#======load vars======
ttfFont = settings.ttfFontFile
pixMM = settings.pixelDensity
board_h = settings.boardHeightmm*pixMM  #int board width should calc in code, meh
board_l = settings.boardLengthmm*pixMM #int board height
curve = settings.fontSizeCurve
fontMax = settings.fontMaxPixHeight
fontMin = settings.fontMinPixHeight
bScale = settings.collisionPixelRadius
centerFile = settings.centerMaskPNG

mm2pix = 1/settings.pixelDensity #12 pixels to 1 mm
decimalPlaces = settings.gCodeDecimals
gFontFile = settings.gCodeFontFile
absBoardY = -settings.boardHeightmm
absBoardX = -settings.boardLengthmm
xPosCal = settings.xPosCalmm
yPosCal = settings.yPosCalmm
border = settings.borderOffset

entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt


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
        print("placer: couldn't open center PNG")
        #sys exit, shut down threads?
    
    backing = Image.new('RGBA', (board_l,board_h), color=(255,255,255,255))
    draw = ImageDraw.Draw(backing)
    
    #overlay center keepout
    print("placer: making virtual backing, secretly")
    center_l, center_h = center.size
    
    centerPos_l = int((board_l / 2) - (center_l / 2))
    centerPos_h = int((board_h / 2) - (center_h / 2))
    
    backing.alpha_composite(center, (centerPos_l, centerPos_h))
    
    #create backing image based on db
    nameWasPlaced = (Sub
                     .select()
                     .where(Sub.status >= placed)
                    )
    
    for place in nameWasPlaced:
        font = ImageFont.truetype(ttfFont, place.fontSize)
        draw.text((place.positionX,place.positionY), place.userName, (0,0,0), font = font)
    
    #check database for names to place
    nameToPlace = (Sub
             .select()
             .where(Sub.status == entered)
             .order_by(Sub.entryTime)
            )
    
    for sub in nameToPlace:
        #LED_TYel.on()
        
        totalEntries = Sub.select().where(Sub.status >= placed).count()
        
        fontSize = fscale(fontMin, fontMax, totalEntries, curve)
        
        blurRad = int(fontSize/bScale) #pixel radius of blur
        
        fail = True
        print("placer: " + sub.userName)
        
        #this should be a function for font choice based on number of existing names
        #the database population function/module/program should do this
        font = ImageFont.truetype(ttfFont, fontSize)
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
            pixOffset = border * pixMM
            Rboard_l = random.randint((0 + pixOffset),(board_l2 - pixOffset))
            Rboard_h = random.randint((0 + pixOffset),(board_h2 - pixOffset))
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
                        print("placer: :failfish:")
                        #LED_TYel.blink()
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
        sub.fontSize = fontSize
        sub.status = placed
        sub.save()
        #LED_TYel.off()
        #makeGcode(sub)

        
def makeGcode(name):
    #print("gCode Maker Running")
    
    #open the font file
    searchFile = open(gFontFile, "r")
    stringFile = searchFile.read()
    
    glyphs = [ c for c in re.finditer(r'unicode="([^"]+)"', stringFile)]
    
    #get constants from font file
    #graphics design exchange says "vert origin x" value is a thing in ttf
    #but no evidence of that in the svg conversion so, using ascent. will tweak.
    ascentEm = float(re.search(r'cap-height="([^"]+)"', stringFile).group(1))
    
    #default horiz adv
    advanceEm = float(re.search(r'horiz-adv-x="([^"]+)"', stringFile).group(1))
    
    #units-per-em
    unitsEm = float(re.search(r'units-per-em="([^"]+)"', stringFile).group(1))
    
    #define gcode block in output file
    print("gMaking: " + name.userName)
    entryString = ""
    
    #do some math
    em2MM = (name.fontSize * mm2pix) / unitsEm
    
    #the y position based on pixel to mm conversion
    #ascent is needed because PIL places in the upper left of the text
    #yCursor = (absBoardY) + (sub.positionY * mm2pix) - (ascentEm * em2MM)   
    yCursor =  ((-1) * name.positionY * mm2pix) - (ascentEm * em2MM) + yPosCal
    xCursor =  (absBoardX) + (name.positionX * mm2pix) + xPosCal
    
    lastChar = None
    hkern = None
    
    for c in name.userName:
        #LED_BYel.on()
        #define our letter in Gcode becaus reasons
        entryString += ("(char = \"" + c + "\")\n")
    
        #find c in the font file
        x = [x for x in range(len(glyphs)) if glyphs[x].group(1) == c]
        x = int(x[0]) #this is annoying
        
        #we need this specifically later but its a location basis to get the gcode lines
        glyphStartPos = glyphs[x].start()
        horizPattern = re.compile(r'horiz-adv-x="([^"]+)"')
        
        #what position in the massive string is the start and end of gcode block
        startPos_Gglyph = stringFile.find('\n', glyphStartPos) + 1
        
        #what about '_' (last char before hkern lines in file)
        #cue: find g and h find the minimum
        gPos = stringFile.find('g', startPos_Gglyph) - 2
        hPos = stringFile.find('h', startPos_Gglyph) - 2
        
        #I could put this in the above but whatever, readability
        endPos_Gglyph = min(gPos,hPos)
        
        #special kern spacing between specific chars at end of file
        if lastChar != None: 
            #build string and regex it eg: hkern u1="Y" u2="v" k="55"
            #float(re.search(r"hkern u1=\"Y\" u2=\"v\" k=\"([^\"]+)\"", stringFile).group(1))
            
            #build regex as a string
            regString = r"hkern u1=\""+ lastChar + "\" u2=\"" + c + "\" k=\"([^\"]+)\""
            try:
                hkern = re.search(regString, stringFile).group(1)
                xCursor -= float(hkern.group(1)) * em2MM #move cursor back no of mm 
            except:
                pass
                            
        #iterate line by line from location to location in the string
        for line in stringFile[startPos_Gglyph:endPos_Gglyph].split('\n'): 
            #print(line)
            sLine = line.strip()
            if sLine:
                g = GParseQuick(sLine)
                
                #scale
                g.set("X", round((g.get("X")* em2MM), decimalPlaces))
                g.set("Y", round((g.get("Y")* em2MM), decimalPlaces))
                
                #translate
                g.set("X", round((xCursor + g.get("X")), decimalPlaces))
                g.set("Y", round((yCursor + g.get("Y")), decimalPlaces))
                
                if g.get("G") == "02" or g.get("G") == "03":
                    g.set("I", round((g.get("I")* em2MM), decimalPlaces))
                    g.set("J", round((g.get("J")* em2MM), decimalPlaces))
                
                #append the line to big string   
                entryString += g.unparse()+"\n"
                
            else:
                #handle blank lines
                entryString += "\n"
            
        #move the cursor horizontally for next char, use default if no special space
        try:
            advanceX = horizPattern.search(stringFile, glyphStartPos, startPos_Gglyph).group(1)
            xCursor += (float(advanceX) * em2MM)
        except: 
            xCursor += (advanceEm * em2MM)
        
        #store for next loop
        lastChar = c
        #LED_BYel.off()
        
    #done with sub
    name.gCode = entryString
    name.status = gcode
    name.save()
    
    #close the font file
    searchFile.close()
    
if __name__ == "__main__":
    placeNames()