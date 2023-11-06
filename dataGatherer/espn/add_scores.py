import requests
import json
from datetime import datetime, timedelta
from dateutil import tz
import numpy as np
import pytz
import sys 
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def convertDateTime(dateTime):
    from_zone = tz.gettz("Africa/Accra")
    to_zone = tz.gettz('America/New_York')
    test = dateTime
    test = test.split("T")[0] + " " + test.split("T")[1].split("Z")[0]
    utc = datetime.strptime(test, "%Y-%m-%d %H:%M")
    utc = utc.replace(tzinfo=from_zone)
    eastern = str(utc.astimezone(to_zone))
    date = eastern.split(" ")[0]
    time = eastern.split(" ")[1].split("-")[0]
    return date, time


def get_scores(date):
    #Get ESPN LIVE SCORE DATA
    try:
        url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard'
        sports_response = requests.get(url,params={'limit':'500','groups':'50','dates': str(date)})
        sports_json = json.loads(sports_response.text)
        espn = {}
        for game in sports_json['events']:
            date = game['competitions'][0]['date']
            date, time = convertDateTime(date)
            siteType = game['competitions'][0]['neutralSite']
            gameId = game['id']
            try:
                broadcast = game['competitions'][0]['broadcasts'][0]['names'][0]
            except:
                broadcast = None
            #team1
            team_type = game['competitions'][0]['competitors'][0]['homeAway']
            if team_type == 'home':
                homeTeam = game['competitions'][0]['competitors'][0]['team']['displayName']
                homeTeamId = game['competitions'][0]['competitors'][0]['team']['id']
                homeScore = game['competitions'][0]['competitors'][0]['score'] 
            else:
                awayTeam = game['competitions'][0]['competitors'][0]['team']['displayName']
                awayTeamId = game['competitions'][0]['competitors'][0]['team']['id']
                awayScore = game['competitions'][0]['competitors'][0]['score']
            #team2    
            team_type = game['competitions'][0]['competitors'][1]['homeAway']
            if team_type == 'home':
                homeTeam = game['competitions'][0]['competitors'][1]['team']['displayName']
                homeTeamId = game['competitions'][0]['competitors'][1]['team']['id']
                homeScore = game['competitions'][0]['competitors'][1]['score']
            else:
                awayTeam = game['competitions'][0]['competitors'][1]['team']['displayName']
                awayTeamId = game['competitions'][0]['competitors'][1]['team']['id']
                awayScore = game['competitions'][0]['competitors'][1]['score']
            #gamedetails
            clock = game['status']['displayClock']
            period = game['status']['period']
            status = game['status']['type']['state']
            espnGame = {
                    "date" : date,
                    "time" : time,
                    "broadcast": broadcast,
                    "siteType": siteType,
                    "clock": clock,
                    "period": period,
                    "status": status,
                    "homeTeam": homeTeam,
                    "homeTeamId": homeTeamId,
                    "homeScore": homeScore,
                    "awayTeam": awayTeam,
                    "awayTeamId": awayTeamId,
                    "awayScore": awayScore,

            }
            espn[gameId] = espnGame
        return espn
    except:
        return {}

def get_db_games(date):
    scores = get_scores(date)
    container = connectToContainer('boxscores')
    qry = f"SELECT * FROM c WHERE c.date = '{date}'"
    games = container.query_items(qry, enable_cross_partition_query=True)
    for game in games:
        try:
            game['homeScore'] = scores[game['id']]['homeScore']
            game['awayScore'] = scores[game['id']]['awayScore']
            game['period'] = scores[game['id']]['period'] 
            game['status'] = scores[game['id']]['status']
        except:
            game['homeScore'] = None
            game['awayScore'] = None
            game['period'] = None
            game['status'] = None
        container.upsert_item(body=game)

if __name__ == "__main__":
    EST = pytz.timezone('America/New_York')
    datetime_est = datetime.now(EST)
    yesterday = datetime_est - timedelta(days=1)
    date = yesterday.strftime('%Y%m%d')
    get_db_games(date)

