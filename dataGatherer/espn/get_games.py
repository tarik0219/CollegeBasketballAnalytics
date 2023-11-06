import requests
import json
from datetime import datetime
from dateutil import tz
import pytz
import sys
import os
import csv
import pickle
import numpy as np
import os

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

def changeBool(value):
    if value:
        return 1
    else:
        return 0

def make_prediction(homeData,awayData,siteType):
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    scoresFile = dir.replace('utils', 'models') + '/scores.pkl'
    probFile = dir.replace('utils', 'models') + '/prob.pkl'
    
    scoresModel = pickle.load(open(scoresFile, 'rb'))
    probModel = pickle.load(open(probFile, 'rb'))

    siteType = changeBool(siteType)

    X = np.array([[homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],siteType]])

    y_pred = scoresModel.predict(X)
    y_pred.tolist()
    y_prob = probModel.predict_proba(X)
    y_prob.tolist()
    

    if siteType == 1:
        X2 = np.array([[awayData['average']['offRating'],awayData['average']['defRating'],awayData['average']['TempoRating'],homeData['average']['offRating'],homeData['average']['defRating'],homeData['average']['TempoRating'],siteType]])

        y_pred_2 = scoresModel.predict(X2)
        y_pred_2.tolist()
        y_prob_2 = probModel.predict_proba(X2)
        y_prob_2.tolist()

        homeScore = round((y_pred[0][0] + y_pred_2[0][1])/2,1)
        awayScore = round((y_pred[0][1] + y_pred_2[0][0])/2,1)
        prob = round((y_prob[0][1]+y_prob_2[0][0])/2,4)
    
    else:
        homeScore = round(y_pred[0][0],1)
        awayScore = round(y_pred[0][1],1)
        prob = round(y_prob[0][1],4)

    return homeScore,awayScore,prob 


def get_games(date):
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard'
    sports_response = requests.get(url,params={
    'limit':'500',
    'groups':'50',
    'dates': date})
    data = json.loads(sports_response.text)
    games = []
    for game in data['events']:
        date = game['competitions'][0]['date']
        date, time = convertDateTime(date)
        date = date.replace("-","")
        siteType = game['competitions'][0]['neutralSite']
        gameId = game['id']
        #team1
        team_type = game['competitions'][0]['competitors'][0]['homeAway']
        if team_type == 'home':
            homeTeamId = game['competitions'][0]['competitors'][0]['team']['id']
            homeScore = game['competitions'][0]['competitors'][0]['score']
        else:
            awayTeamId = game['competitions'][0]['competitors'][0]['team']['id']
            awayScore = game['competitions'][0]['competitors'][0]['score']
        #team2    
        team_type = game['competitions'][0]['competitors'][1]['homeAway']
        if team_type == 'home':
            homeTeamId = game['competitions'][0]['competitors'][1]['team']['id']
            homeScore = game['competitions'][0]['competitors'][1]['score']
        else:
            awayTeamId = game['competitions'][0]['competitors'][1]['team']['id']
            awayScore = game['competitions'][0]['competitors'][1]['score']
        espnGame = {
                "id":gameId,
                "date" : date,
                "siteType": siteType,
                "homeTeamId": homeTeamId,
                "awayTeamId": awayTeamId,
                'homeScore': homeScore,
                'awayScore':awayScore
        }
        games.append(espnGame)
    return games

def add_odds(games):
    for count,game in enumerate(games):
        url = f'https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/{game["id"]}/competitions/{game["id"]}/odds'
        odds_response = requests.get(url)
        odds_json = json.loads(odds_response.text)
        if len(odds_json['items']) != 0:
            games[count]['line'] = odds_json['items'][0]['spread']
            games[count]['overUnder'] = odds_json['items'][0]['overUnder']
        else:
            games[count]['line'] = None
            games[count]['overUnder'] = None
    return games

def add_team_data(teamsTable,query,games):
    for count,game in enumerate(games):
        homeData = teamsTable.search(query.id == game['homeTeamId'])
        awayData = teamsTable.search(query.id == game['awayTeamId'])
        if len(homeData) != 0:
            games[count]['homeTeamData'] = homeData[0]
        if len(awayData) != 0:
            games[count]['awayTeamData'] = awayData[0]
    return games

def add_prediction(fileName,games):
    for game in games:
        if "homeTeamData" in game and "awayTeamData" in game:
            homescore,awayscore,prob = make_prediction(game['homeTeamData'],game['awayTeamData'],game['siteType'])
            data = {
                'id':game['id'],
                'date':game['date'],
                'site':game['siteType'],
                'hoff':game['homeTeamData']['average']['offRating'],
                'hdef':game['homeTeamData']['average']['defRating'],
                'htemp':game['homeTeamData']['average']['TempoRating'],
                'aoff':game['awayTeamData']['average']['offRating'],
                'adef':game['awayTeamData']['average']['defRating'],
                'atemp':game['awayTeamData']['average']['TempoRating'],
                'line':game['line'],
                'ou':game['overUnder'],
                'hp':homescore,
                'ap':awayscore,
                'prob':prob
            }
            add_row_to_csv(fileName, data)
    return games


def add_row_to_csv(csv_filename, data_dict):
    try:
        existing_ids = set()
        # Read the existing headers from the CSV file
        with open(csv_filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)
            for row in csv_reader:
                existing_ids.add(row[0])

        # Check if the provided ID exists in the CSV
        if 'id' in data_dict and data_dict['id'] in existing_ids:
            print(f"Row with ID '{data_dict['id']}' already exists in the CSV.")
            return

        # Ensure that all headers in the CSV are present in the dictionary
        for header in headers:
            if header not in data_dict:
                data_dict[header] = ''  # Set missing headers to blank

        # Append the data from the dictionary to the CSV file
        with open(csv_filename, 'a', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
            csv_writer.writerow(data_dict)

        print("Row added to CSV successfully.")
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def replace_row_in_csv(csv_filename, new_data):
    try:
        # Read the existing data from the CSV file and find the row with the matching ID
        rows = []
        row_found = False

        with open(csv_filename, 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            headers = csv_reader.fieldnames

            for row in csv_reader:
                if row['id'] == new_data['id']:
                    row['hs'] = new_data['homeScore']
                    row['as'] = new_data['awayScore']
                    rows.append(row)
                    row_found = True
                else:
                    rows.append(row)

        # If the row with the specified ID was not found, return an error
        if not row_found:
            print(f"Row with ID '{new_data['id']}' not found in CSV.")
            return

        # Write the updated data back to the CSV file
        with open(csv_filename, 'w', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
            csv_writer.writeheader()
            csv_writer.writerows(rows)

        print(f"Row with ID '{new_data['id']}' replaced in CSV.")
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def add_scores(date,csv_filename):
    games = get_games(date)
    for game in games:
        replace_row_in_csv(csv_filename, game)

if __name__ == "__main__":
    EST = pytz.timezone('America/New_York')
    datetime_est = datetime.now(EST)
    date = datetime_est.strftime('%Y%m%d')
    games = get_games(date)
    games = add_odds(games)
    games = add_team_data(games)
    games = add_prediction(games)