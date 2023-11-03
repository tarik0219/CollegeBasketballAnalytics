from tinydb import TinyDB, Query
from tinydb.operations import set
import os

dbfile = os.path.join(os.getcwd(), "cbbweb.json")


def get_db():
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable

db = TinyDB(dbfile)
query = Query()
teamsTable = db.table('teams')