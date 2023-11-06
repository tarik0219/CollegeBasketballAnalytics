# main_script.py
import sys
sys.path.append("..")  # Add the parent directory (project) to the Python path
import json
from kenpom import kenpom
from barttorvik import barttorvik
from calculate import calculate
from tinydb import TinyDB, Query
from tinydb.operations import set

db = TinyDB('cbbweb.json')
query = Query()
teamsTable = db.table('teams')

with open("conf_kp_sportsreference.json") as json_file:
    conf_kp_sportsreference = json.load(json_file)


kenpomTeams = kenpom.UpdateKenpom()

#Update Kenpom Stats
for team in kenpomTeams:
    conf = conf_kp_sportsreference[team['conference']]
    try:
        teamsTable.update(set("conference", conf), query.id == team['id'])
    except:
        print(team)
        pass