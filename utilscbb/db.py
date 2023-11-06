from tinydb import TinyDB, Query
import os
from utilscbb.constants import dbFileName,PAdbFileName

dbfile = os.path.join(os.getcwd(), dbFileName)

PAdbfile = os.path.join(os.getcwd(), PAdbFileName)
def get_db_pa():
    print(dbfile)
    db = TinyDB(PAdbfile)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable

def get_db():
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable



try:
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
except:
    pass