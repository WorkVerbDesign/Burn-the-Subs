# Let's make an database
#
# this is like the worst code ever
#
# just to make an test DB for burn the subs
# returns the number of entries it creates.

from datetime import datetime
from dataBaseClass import Sub
import os, time, random

def makeDb():
    fileName = open("subscriberListTest.txt")
    count = 0

    for entry in fileName:
        entry = entry.strip()
        dateTime = datetime.utcnow()
        count += 1
        dbEntry = Sub.create(
                                userName = entry,
                                entryTime = dateTime
                            )
        dbEntry.save()
        print("dbmaker: " + entry)
        #time.sleep(random.randint(10,100)) #up to 10 seconds for testing
    
    print("dbMaker: done, you fuck.")
    fileName.close()
    return count

if __name__ == "__main__":
    makeDb()