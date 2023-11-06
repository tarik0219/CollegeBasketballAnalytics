import requests
import json
from datetime import datetime
from dateutil import tz
import pickle
import numpy as np
import warnings
import pytz
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilscbb.predict import make_prediction
from utils.connectDb import connectToDB
from tinydb.operations import set
from multiprocessing import Pool

def check_conference_tournament(date, conference):
    # Load the JSON file with conference tournament dates
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    conference_tournaments_file = dir.replace('schedule', 'dicts') + '/conference_tournaments_2023.json'
    with open(conference_tournaments_file, 'r') as f:
        tournament_dates = json.load(f)
    # Check if the conference is in the JSON file
    if conference not in tournament_dates:
        return False
    # Convert the date string to a datetime object for comparison
    date = datetime.strptime(date, "%Y-%m-%d")
    # Check if the date falls within the start and end dates of the conference's tournament
    start_date = datetime.strptime(tournament_dates[conference]["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(tournament_dates[conference]["end_date"], "%Y-%m-%d")
    if start_date <= date <= end_date:
        return True
    else:
        return False

def check_after_conference_tournament(date, conference):
    # Load the JSON file with conference tournament dates
    with open('conference_tournaments_2023.json') as f:
        tournament_dates = json.load(f)
    
    # Check if the conference is in the JSON file
    if conference not in tournament_dates:
        return False
    
    # Convert the date string to a datetime object for comparison
    date = datetime.strptime(date, "%Y-%m-%d")
    
    # Check if the date falls after the end date of the conference's tournament
    end_date = datetime.strptime(tournament_dates[conference]["end_date"], "%Y-%m-%d")
    if date > end_date:
        return True
    else:
        return False

def is_date_in_past(date_str):
    # Create a timezone object for Eastern Time
    eastern = pytz.timezone("US/Eastern")
    
    # Convert the date string to a datetime object
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Get the current date in Eastern Time
    now_eastern = datetime.now(eastern).date()
    
    # Return whether the given date is older than the current date
    return date < now_eastern


def get_team_data(year):
    team_data = {}
    all_records = []
    #container = connectToContainer('Teams')
    #data = container.read_all_items()
    teamsTable, query = connectToDB()
    data = teamsTable.all()
    for team in data:
        team_data[team['id']] = team
    for key in team_data:
        print(team_data[key]['teamName'])
        data = combine_schedule(key, year, team_data)
        records = calculate_records(data)
        records['id'] = key
        all_records.append(records)
    return all_records



# def get_line_data(ids):
#     boxscores = {}
#     container = connectToContainer('boxscores')
#     qry = f"""SELECT
#             *
#             FROM  c
#             WHERE c.id IN ({(', '.join('"' + item + '"' for item in ids))})"""
#     scores = container.query_items(qry, enable_cross_partition_query=True)
#     try:
#         for team in scores:
#             boxscores[team['id']] = team
#     except:
#         pass
#     return boxscores

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


def get_schedule(id,year):
    season_count = 2
    data = []
    ids = []
    while (season_count < 4):
        url = f'https://site.web.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{id}/schedule'
        sports_response = requests.get(url,params={'season':year,'seasontype':str(season_count)})
        sports_json = json.loads(sports_response.text)
        try:
            for game in sports_json['events']: 
                game_data = {}
                date,time = convertDateTime(game["date"])
                game_data['date'] = date
                game_data['gameId'] = game["id"]
                ids.append(game["id"])
                game_data['siteType'] = game['competitions'][0]["neutralSite"]
                try:
                    game_data['seasonType'] = game['competitions'][0]["type"]['abbreviation']
                except:
                    game_data['seasonType'] = 'POST'
                game_data['completetd'] = game['competitions'][0]['status']['type']['completed']
                if game['competitions'][0]['competitors'][0]["id"] == id:
                    if game_data['siteType']:
                        game_data['venue'] = "N"
                    elif game['competitions'][0]['competitors'][0]["homeAway"] == "home":
                        game_data['venue'] = "H"
                    else:
                        game_data['venue'] = "@"
                    if game_data['completetd']:
                        game_data['score'] = game['competitions'][0]['competitors'][0]["score"]['displayValue']
                        game_data['opponentScore'] = game['competitions'][0]['competitors'][1]["score"]['displayValue']
                    game_data['opponentId'] = game['competitions'][0]['competitors'][1]["id"]
                    game_data['opponentName'] = game['competitions'][0]['competitors'][1]['team']["displayName"]
                else:
                    if game_data['siteType']:
                        game_data['venue'] = "N"
                    elif game['competitions'][0]['competitors'][0]["homeAway"] == "home":
                        game_data['venue'] = "@"
                    else:
                        game_data['venue'] = "H"
                    if game_data['completetd']:
                        game_data['score'] = game['competitions'][0]['competitors'][1]["score"]['displayValue']
                        game_data['opponentScore'] = game['competitions'][0]['competitors'][0]["score"]['displayValue']
                    game_data['opponentId'] = game['competitions'][0]['competitors'][0]["id"]
                    game_data['opponentName'] = game['competitions'][0]['competitors'][0]["team"]["displayName"]
                #Game Result (W,L,"")
                if game_data['completetd']:
                    if int(game_data['opponentScore']) > int(game_data['score']):
                        game_data['result'] = "L"
                    elif int(game_data['opponentScore']) < int(game_data['score']):
                        game_data['result'] = "W"
                    else:
                        game_data['result'] = ""
                else:
                    game_data['result'] = ""

                if is_date_in_past(game_data['date']) and game_data['completetd'] == False:
                    pass
                else:
                    data.append(game_data)
        except:
            pass
        season_count += 1
    return data,ids

def combine_schedule(id, year, team_data):
    data, ids = get_schedule(id, year)
    #line_data = get_line_data(ids)
    for count,game in enumerate(data):
        try:
            data[count]["data"] = team_data[id]
            data[count]["opponentData"] = team_data[game['opponentId']]
            if data[count]['seasonType'] == 'POST':
                data[count]['gameType'] = "POST"
            elif data[count]['data']['conference'] == data[count]['opponentData']['conference']:
                # if check_conference_tournament(data[count]['date'], data[count]['data']['conference']):
                #     data[count]['gameType'] = "CTRN"
                # elif check_after_conference_tournament(data[count]['date'], data[count]['data']['conference']):
                #     data[count]['gameType'] = "POST"
                # else:
                data[count]['gameType'] = "CONF"
            else:
                data[count]['gameType'] = "REG"
        except:
            data[count]["opponentData"] = None
            data[count]["data"] = None
            data[count]['gameType'] = "REG"

        if data[count]['completetd'] == False and 'opponentData' in data[count] and data[count]['data'] != None:
            if data[count]['venue'] == "H":
                homescore,awayscore,prob = make_prediction(data[count]['data'], data[count]['opponentData'], data[count]["siteType"])
                data[count]['scorePrediction'] = homescore
                data[count]['opponentScorePrediction'] = awayscore
                data[count]['prob'] = round(prob * 100, 2)
            elif data[count]['venue'] == "@":
                homescore,awayscore,prob = make_prediction(data[count]['opponentData'], data[count]['data'], data[count]["siteType"])
                data[count]['scorePrediction'] = awayscore
                data[count]['opponentScorePrediction'] = homescore
                data[count]['prob'] = 100 - round(prob * 100, 2)
            else:
                homescore,awayscore,prob = make_prediction(data[count]['data'], data[count]['opponentData'], data[count]["siteType"])
                data[count]['scorePrediction'] = homescore
                data[count]['opponentScorePrediction'] = awayscore
                data[count]['prob'] = round(prob * 100, 2)
        elif data[count]['completetd'] == False:
            data[count]['prob'] = 99.00
    return data

def simulate(probs):
    games = len(probs)
    wins = 0
    confGames = len(list(filter(lambda x: x[1] == "CONF", probs)))
    confWin = 0
    for prob in probs:
        if prob[3] != '-1':
            wins = prob[0] * .01 + wins
            if prob[1] == "CONF": 
                confWin = prob[0] * .01 + confWin
    wins = round(wins)
    loss = games - wins
    confWin = round(confWin)
    confLoss = confGames - confWin
    return wins,loss,confWin,confLoss

def calculate_records(data):
    records = {
        "win" : 0,
        "loss": 0,
        "projectedWin":0,
        "projectedLoss":0,
        "confWin" : 0,
        "confLoss": 0,
        "confProjectedWin":0,
        "confProjectedLoss":0
    }
    probs = []
    for game in data:
        if game['completetd']:
            if game['gameType'] == 'CONF':
                if game['result'] == 'W':
                    records['win'] += 1
                    records['confWin'] += 1
                if game['result'] == 'L':
                    records['loss'] += 1
                    records['confLoss'] += 1
            else:
                if game['result'] == 'W':
                    records['win'] += 1
                if game['result'] == 'L':
                    records['loss'] += 1
        else:
            probs.append((game['prob'], game['gameType'], game['opponentName'], game['opponentId']))
    wins,loss,confWin,confLoss = simulate(probs)
    records['projectedWin'] = wins + records['win']
    records['projectedLoss'] = loss + records['loss']
    records['confProjectedWin'] = confWin + records['confWin']
    records['confProjectedLoss'] = confLoss + records['confLoss']
    records['probs'] = probs
    return records

def add_records_teams(data):
    teamsTable, query = connectToDB()
    for team in data:
        teamsTable.update(set("record", team), query.id == team['id'])


if __name__ == "__main__":
    warnings.filterwarnings('ignore') 
    year = "2024"
    data = get_team_data(year)

    teamsTable, query = connectToDB()
    data = teamsTable.all()
    team_data = {}
    for team in data:
        team_data[team['id']] = team
    add_records_teams(data)


