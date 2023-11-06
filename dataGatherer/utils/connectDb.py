from tinydb import TinyDB, Query
from tinydb.operations import set

def connectToDB():
    db = TinyDB('../tiny_db/cbbweb.json')
    query = Query()
    teamsTable = db.table('teams')

    return teamsTable,query