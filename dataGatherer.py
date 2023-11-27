from dataGatherer.kenpom import kenpom
from dataGatherer.barttorvik import barttorvik
from dataGatherer.calculate import calculate
from tinydb.operations import set
from tinydb import TinyDB, Query
import os
from utilscbb import db
from utilscbb import constants
from dataGatherer.espn import get_games
from dataGatherer.espn import add_scores
import datetime
import warnings
from dataGatherer.record import schedule
from utilscbb.constants import year, PAcacheFileName, PAcacheFileNameCopy
from utilscbb.cahce import get_cache
import requests
import json

# Ignore all warnings
warnings.filterwarnings("ignore")


current_date = datetime.datetime.now()
date_string = current_date.strftime("%Y%m%d")
previous_date = current_date - datetime.timedelta(days=1)
previous_date = previous_date.strftime("%Y%m%d")

try:
    query,teamsTable = db.get_db_pa()
except:
    query,teamsTable = db.get_db()

print('Getting Kenpom Data')
kenpomTeams = kenpom.UpdateKenpom()
print('Retrieved Kenpom Data')

print('Getting Barttorvik Data')
barttorvikTeams = barttorvik.UpdateBart()
print('Retrieved Barttorvik Data')



#Update Kenpom Stats
print('Updating Kenpom Data in DB')
for team in kenpomTeams:
    try:
        teamsTable.update(set("kenpom", team), query.id == team['id'])
    except:
        if bool(team):
            print(team)
        pass
print('Updated Kenpom Data')

#Update Bart Stats
print('Updating Barttorvik Data in DB')
for team in barttorvikTeams:
    try:
        teamsTable.update(set("barttorvik", team), query.id == team['id'])
    except:
        if bool(team):
            print(team)
        pass
print('Updated Bart Data')

#calculate averages
try:
    calculate.updateStats(query,teamsTable)
except Exception as e:
    print("Unable to calculate Stats Error: ", e)

#calculate records
print("Calculating Records")
try:
    schedule.add_records_teams(year,teamsTable,query)
    print("Calculated Records")
except Exception as e:
    print("Unable to calculate records Error: ", e)


#Add to cache
def add_to_cache_line_data(games):
    print("Adding to cache")
    query, cache = get_cache()
    for game in games:
        gameId = game['id']
        url = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/{}/competitions/{}/odds?=".format(gameId, gameId)
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        cache.upsert(
            {
                "gameId": gameId,
                "response": json.dumps(response.json())
            }
        )
    print("Added to cache")
    return

#Add to model
try:
    gamesFile = os.path.join(os.getcwd(), constants.PAdataFile)
    games = get_games.get_games(date_string)
    add_to_cache_line_data(games)
    games = get_games.add_odds(games)
    games = get_games.add_team_data(teamsTable,query,games)
    games = get_games.add_prediction(gamesFile,games)
    print('Added Games')
except Exception as e:
    print("Did not add games Error: ", e)


try:    
    get_games.add_scores(previous_date,gamesFile)
    print('Added Scores')
except Exception as e:
    print("Did not add previous day scores Error: ", e)