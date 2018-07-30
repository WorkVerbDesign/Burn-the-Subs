# Let's make an database
#
# this is like the worst code ever
#
# just to make an test DB for burn the subs

from datetime import datetime
from dbShit import Sub
import os, time

def main():
    fileName = open("subscriberListTest.txt")
    print("making:")
    for entry in fileName:
        entry = entry.strip()
        dateTime = datetime.utcnow()
        
        dbEntry = Sub.create(
            userName = entry,
            entryTime = dateTime,
            status = 2,
            userName = 'Yfj',
            fontSize = 72,
            positionX = 1000,
            positionY = 1000
        )
        
        print(entry)
        time.sleep(0.2)
        dbEntry.save()
    
    print("done, you fuck.")
    fileName.close()

if __name__ == "__main__":
    main()