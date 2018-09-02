# db unparser
# scans db for placed names
# creates output.txt
# which is just a butt-ton of gcode
# status = 0: name entered 1: name placed 2:gcode ready 3: burnt to board

import settings
from dataBaseClass import Sub
placed = settings.namePlaced

outputFile = settings.gCodeFile

def unParsify():
    output = open(outputFile, "a")

    nameToMake = (Sub
                     .select()
                     .where(Sub.status >= placed)
                     .order_by(Sub.entryTime)
                    )
    
    for sub in nameToMake:
        print("gcodifying: " + sub.userName)
        output.write("(Block-name: " + sub.userName + ")\n")
        output.write(sub.gCode)
                    
    output.close()

if __name__ == "__main__":
    unParsify()