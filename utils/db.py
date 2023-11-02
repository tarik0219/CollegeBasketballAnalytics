from tinydb import TinyDB, Query
from tinydb.operations import set
import os

dbfile = os.path.join(os.getcwd(), "cbbweb.json")


db = TinyDB(dbfile)
query = Query()
teamsTable = db.table('teams')