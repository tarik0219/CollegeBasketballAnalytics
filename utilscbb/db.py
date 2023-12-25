from tinydb import TinyDB, Query
import os
from utilscbb.constants import dbFileName,PAdbFileName, dbFileNameCopy, cacheFileNameCopy, PAdbFileNameCopy, PAcacheFileNameCopy
import shutil

dbfile = os.path.join(os.getcwd(), dbFileName)
dbFileCopy = os.path.join(os.getcwd(), dbFileNameCopy)
padbfile = os.path.join(os.getcwd(), PAdbFileName)
PAdbfilecopy = os.path.join(os.getcwd(), PAdbFileNameCopy)

def get_db(filename):
    db = TinyDB(filename)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable


    



try:
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
except:
    pass