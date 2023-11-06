# main_script.py
import sys
sys.path.append("..")  # Add the parent directory (project) to the Python path

from kenpom import kenpom
from barttorvik import barttorvik
from calculate import calculate
from tinydb import TinyDB, Query
from tinydb.operations import set


db = TinyDB('cbbweb.json')
query = Query()
teamsTable = db.table('teams')



kenpomTeams = kenpom.UpdateKenpom()
barttorvikTeams = barttorvik.UpdateBart()

#Update Kenpom Stats
for team in kenpomTeams:
    try:
        teamsTable.update(set("kenpom", team), query.id == team['id'])
    except:
        print(team)
        pass

#Update Bart Stats
for team in barttorvikTeams:
    try:
        teamsTable.update(set("barttorvik", team), query.id == team['id'])
    except:
        print(team)
        pass

calculate.updateStats()

print(teamsTable.search(query.id == '2509')[0])