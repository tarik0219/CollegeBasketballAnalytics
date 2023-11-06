import requests
import json
from datetime import datetime
from dateutil import tz
from utilscbb.cahce import get_cache


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
    

def get_half(period):
    if period == 1:
        return "1st"
    elif period == 2:
        return "2nd"
    elif period == 3:
        return "OT"
    elif period == 4:
        return "2OT" 
    elif period == 5:
        return "3OT" 
    elif period == 6:
        return "4OT" 
    elif period == 7:
        return "5OT" 
    elif period == 8:
        return "6OT" 
    elif period == 9:
        return "7OT" 
    elif period == 10:
        return "8OT" 
    elif period == 10:
        return "9OT"   

def get_espn_boxscore(gameId):
    homeData = []
    awayData = []
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary"
    sports_response = requests.get(url,params={'event':gameId })
    sports_json = json.loads(sports_response.text)
    home = sports_json['boxscore']['players'][1]
    away = sports_json['boxscore']['players'][0]
    labels = home['statistics'][0]['labels']
    for player in home['statistics'][0]['athletes']:
        player_stats = {
            "name" : player['athlete']['displayName'],
            "starter":player['starter']
        }
        stats = player['stats']
        for s, l in zip(stats, labels): 
            if l == "3PT":
                player_stats["TPT"] = s
            else:
                player_stats[l] = s
        homeData.append(player_stats)
    
    for player in away['statistics'][0]['athletes']:
        player_stats = {
            "name" : player.get('athlete', {}).get('displayName', None), 
            "starter":player['starter']
        }
        stats = player['stats']
        for s, l in zip(stats, labels): 
            if l == "3PT":
                player_stats["TPT"] = s
            else:
                player_stats[l] = s
        awayData.append(player_stats)
    return homeData, awayData


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
                    "half":get_half(period)
            }

            espn[gameId] = espnGame


        return espn
    except:
        return {}
    
def get_line_data(gameId):
    query, cache = get_cache()
    cahceResponse = cache.search(query.gameId == gameId)
    if len(cahceResponse) != 0:
        return json.loads(cahceResponse[0]["response"])
    url = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/{}/competitions/{}/odds?=".format(gameId,gameId)
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    cache.insert(
        {
            "gameId":gameId,
            "response": json.dumps(response.json())
        }
    )
    return response.json()