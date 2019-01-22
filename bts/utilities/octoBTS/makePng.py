# make a .png image sequence
# from the burn the subs database
# one frame per second or something

from PIL import Image
from PIL import ImageFont, ImageDraw

from . import settings
from .dataBaseClass import Sub

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

entered = settings.nameEntered
placed = settings.namePlaced
gcode = settings.nameGcode
burnt = settings.nameBurnt

#size of png output files, w,h in pizxaacedsac
#size = (16704, 4080)
#size = (4096, 1000)
#size = (1920, 469)

def makeOnePng():
    try:
        #I changed this to use the nice looking board backing
        #the main code uses the center.png regular from settings.py
        center = Image.open("centerFancy.png")
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
                     .order_by(Sub.entryTime)
                    )
    #i = 0
    #filename = "sequence png/sequence%03d.png" % (i,)
    #reBacking = backing.resize(size,Image.LANCZOS)
    #nuBacking = Image.new('RGBA', (1920,1080), color=(0,0,0,0))
    #nuBacking.alpha_composite(reBacking, (0,305))
    #nuDraw = ImageDraw.Draw(nuBacking)
    #userNumText = "Entries: 000"
    #nuFont = ImageFont.truetype(ttfFont, 72)
    #nuDraw.text((5,800), userNumText, (255,255,255), font = nuFont)
    #nuBacking.save(filename)
    #reBacking.save(filename)
    #backing.save("sequence png/sequence_unscale.png")
    #i = 1
    
    for place in nameWasPlaced:
        font = ImageFont.truetype(ttfFont, place.fontSize)
        draw.text((place.positionX,place.positionY), place.userName, (0,0,0), font = font)

        #write the test image of the board
        #print("printing output")
        #filename = "sequence png/sequence%03d.png" % (i,)
        #reBacking = backing.resize(size,Image.LANCZOS)
        
        #nuBacking = Image.new('RGBA', (1920,1080), color=(48,48,48,255))
        #nuBacking.alpha_composite(reBacking, (0,305))
        #nuDraw = ImageDraw.Draw(nuBacking)
        #userNumText = "Entries: %03d" % (i,)
        #nuFont = ImageFont.truetype(ttfFont, 72)
        #nuDraw.text((5,800), userNumText, (255,255,255), font = nuFont)
        #l,h = nuFont.getsize(place.userName)
        #position = (1920 - 5) - l        
        #nuDraw.text((position, 800), place.userName, (255,255,255), font = nuFont, anchor = 'Right')
        #nuBacking.save(filename)
        #i += 1
        
    print("printing output")
    filename = "output.png"
    backing.save(filename)
    
    
if __name__ == "__main__":
    makeOnePng()