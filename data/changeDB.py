from tinydb import TinyDB, Query
from tinydb.operations import set


db = TinyDB('cbbweb.json')
query = Query()
teamsTable = db.table('teams')

data = teamsTable.all()

for team in data:
    teamsTable.update(set("record", ""), query.id == team['id'])