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

# Ignore all warnings
warnings.filterwarnings("ignore")


current_date = datetime.datetime.now()
date_string = current_date.strftime("%Y%m%d")
previous_date = current_date - datetime.timedelta(days=1)
previous_date = previous_date.strftime("%Y%m%d")

query,teamsTable = db.get_db()

kenpomTeams = kenpom.UpdateKenpom()
barttorvikTeams = barttorvik.UpdateBart()

#Update Kenpom Stats
for team in kenpomTeams:
    try:
        teamsTable.update(set("kenpom", team), query.id == team['id'])
    except:
        if len(team) != 0:
            print(team)
        pass
print('Updated Kenpom Data')

#Update Bart Stats
for team in barttorvikTeams:
    try:
        teamsTable.update(set("barttorvik", team), query.id == team['id'])
    except:
        if len(team) != 0:
            print(team)
        pass
print('Updated Bart Data')

#calculate averages
try:
    calculate.updateStats(query,teamsTable)
except:
    print("Unable to calculate Stats")
    pass



try:
    gamesFile = os.path.join(os.getcwd(), constants.dataFile)
    games = get_games.get_games(date_string)
    games = get_games.add_odds(games)
    games = get_games.add_team_data(teamsTable,query,games)
    games = get_games.add_prediction(gamesFile,games)
    print('Added Games')
except:
    print("Did not add games")


try:    
    get_games.add_scores(previous_date,gamesFile)
    print('Added Scores')
except:
    print("Did not add previous day scores")



