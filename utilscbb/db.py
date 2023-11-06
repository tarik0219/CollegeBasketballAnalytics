from tinydb import TinyDB, Query
import os
from utilscbb.constants import dbFileName

dbfile = os.path.join(os.getcwd(), dbFileName)

def get_db():
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable

db = TinyDB(dbfile)
query = Query()
teamsTable = db.table('teams')