# db shit goes here
# so if we want to change anything on the fly
# we don't have to edit like 7 programs.
# this is from: with help from: cordain99 etc
# status = 0: name entered 1: name placed 2:gcode ready 3: burnt to board

from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

from bts import settings

dbFile = settings.dataBaseFile
db = SqliteQueueDatabase(dbFile)
entered = settings.nameEntered
#db.atomic('IMMEDIATE')

class Sub(Model):
    status = IntegerField(default = entered)
    userName = CharField()
    fontSize = IntegerField(default = 0)
    positionX = IntegerField(default = 0)
    positionY = IntegerField(default = 0)
    gCode = CharField(default = "")
    entryTime = DateTimeField()
    
    class Meta:
        database = db

db.create_tables([Sub])