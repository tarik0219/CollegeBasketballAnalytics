from tinydb import TinyDB, Query
import os
from utilscbb.constants import dbFileName,PAdbFileName

dbfile = os.path.join(os.getcwd(), dbFileName)

PAdbfile = os.path.join(os.getcwd(), dbFileName)
def get_db_pa():
    db = TinyDB(PAdbfile)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable

def get_db():
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable




db = TinyDB(dbfile)
query = Query()
teamsTable = db.table('teams')