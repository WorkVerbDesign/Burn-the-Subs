#
# gCode maker
#
# 7/16/18
# need to make this append database with gcode!!!
# lines -> charfield (string)
#
# gcode streamer can then pull lines from the string! GENIOUS
#
# parsing values to scale/position
# based on test.db
# using cueXXIII's gcode parser
# https://graphicdesign.stackexchange.com/questions/37127/svg-font-units-per-em-to-mm

import re

from .. import settings
from ..dataBaseClass import Sub
from ..gCodeParser import GParseQuick

#============= Constants ============
mm2pix = 1/settings.pixelDensity #12 pixels to 1 mm
decimalPlaces = settings.gCodeDecimals
fontFile = settings.gCodeFontFile
absBoardY = -settings.boardHeightmm
absBoardX = -settings.boardLengthmm
xPosCal = settings.xPosCalmm
yPosCal = settings.yPosCalmm

def makeGcode():
    print("gCode Maker Running")

    #open the font file
    searchFile = open(fontFile, "r")
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
    
    #list of names
    nameToMake = (Sub
                     .select()
                     .where(Sub.status == 1)
                     .order_by(Sub.entryTime)
                    )
                    
    #if nameToMake == None:
        #print("didn't find nobody")
                    
    for sub in nameToMake:
        #define gcode block in output file
        print("making gcode for: " + sub.userName)
        entryString = ""
        
        #do some math
        #em2MM = (sub.fontSize * point) / unitsEm
        em2MM = (sub.fontSize * mm2pix) / unitsEm
        
        #the y position based on pixel to mm conversion
        #ascent is needed because PIL places in the upper left of the text
        #yCursor = (absBoardY) + (sub.positionY * mm2pix) - (ascentEm * em2MM)   
        yCursor =  ((-1) * sub.positionY * mm2pix) - (ascentEm * em2MM) + yPosCal
        xCursor =  (absBoardX) + (sub.positionX * mm2pix) + xPosCal
        
        lastChar = None
        hkern = None
        
        for c in sub.userName:
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
                    
                    #for the sake of testing    
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
            
        #done with sub
        sub.gCode = entryString
        sub.status = 2
        sub.save()
    
    #close the font file
    print("gCode maker finished")
    searchFile.close()
    
    
if __name__ == "__main__":
    makeGcode()