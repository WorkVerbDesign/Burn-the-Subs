# make a .png image 
# from the burn the subs database
from PIL import Image
from PIL import ImageFont, ImageDraw
from dataBaseClass import Sub
import settings

pixMM = settings.pixelDensity
board_h = settings.boardHeightmm*pixMM   #int board width should calc in code, meh
board_l = settings.boardLengthmm*pixMM #int board height
fontFile = settings.ttfFontFile

def main():  
    #change when parking lot is generated for visual.
    center = Image.open('center.png')
    
    backing = Image.new('RGBA', (board_l,board_h), color=(255,255,255,255))
    draw = ImageDraw.Draw(backing)
    
    center_l, center_h = center.size
    
    centerPos_l = int((board_l / 2) - (center_l / 2))
    centerPos_h = int((board_h / 2) - (center_h / 2))  
    
    backing.alpha_composite(center, (centerPos_l, centerPos_h))    
    
    nameToPlace = (Sub
                   .select()
                   .where(Sub.status >= 0)
                   )
                   
    for sub in nameToPlace:
        print("placing: " + sub.userName)
        font = ImageFont.truetype(fontFile, sub.fontSize)
        draw.text((sub.positionX,sub.positionY), sub.userName, (0,0,0), font = font)
    
    #write the test image of the board
    print("printing output")
    backing.save("test.png")
    
    
    
if __name__ == "__main__":
    main()