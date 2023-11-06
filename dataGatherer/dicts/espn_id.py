import requests
import json
from tinydb import TinyDB, Query
from tinydb.operations import set

db = TinyDB('cbbweb.json')
query = Query()
teamsTable = db.table('teams')

# url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams?limit=500"

# payload={}
# headers = {}

# response = requests.request("GET", url, headers=headers, data=payload)
# teams = response.json()['sports'][0]["leagues"][0]['teams']

# id_espn = {}
# for team in teams:
#     team = team['team']
#     id_espn[team['id']] = team['displayName']

# with open('id_espn.json', 'w') as fp:
#     json.dump(id_espn, fp)


with open("id_espn.json") as json_file:
    id_espn = json.load(json_file)

data = teamsTable.all()

for team in data: 
    try:
        team['teamName'] = id_espn[team['id']]
        teamsTable.upsert(team, query.id == team['id'])
    except:
        print(team)
        print("-------------")
        pass
    


