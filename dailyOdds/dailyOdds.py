from flask import Blueprint, render_template, request
import warnings
from constants import constants
from datetime import datetime, timedelta
from utilscbb.api import get_odds_oddsAPI
import json

# Ignore all warnings
warnings.filterwarnings("ignore")


dailyOdds = Blueprint('dailyOdds', __name__)


def get_best_odds(finalOdds, selectedSportsBooks):
    bestOdds = []
    for game in finalOdds:
        if game['status'] != 'pre':
            continue
        odds = {}
        odds['homeTeamName'] = game['homeTeamName']
        odds['awayTeamName'] = game['awayTeamName']
        odds['prob'] = game['prob']
        homeTeamOdds = 1
        awayTeamOdds = 1
        homeTeamOddsSite = ''
        awayTeamOddsSite = ''
        for sportsBook in game['bookmakers']:
            if sportsBook['key'] not in selectedSportsBooks:
                continue
            if sportsBook['markets'][0]['outcomes'][1]['name'] == game['homeTeamName']:
                if sportsBook['markets'][0]['outcomes'][1]['price'] > homeTeamOdds:
                    homeTeamOdds = sportsBook['markets'][0]['outcomes'][1]['price']
                    homeTeamOddsSite = sportsBook['title']
                if sportsBook['markets'][0]['outcomes'][0]['price'] > awayTeamOdds:
                    awayTeamOdds = sportsBook['markets'][0]['outcomes'][0]['price']
                    awayTeamOddsSite = sportsBook['title']
            else:
                if sportsBook['markets'][0]['outcomes'][0]['price'] > homeTeamOdds:
                    homeTeamOdds = sportsBook['markets'][0]['outcomes'][0]['price']
                    homeTeamOddsSite = sportsBook['title']
                if sportsBook['markets'][0]['outcomes'][1]['price'] > awayTeamOdds:
                    awayTeamOdds = sportsBook['markets'][0]['outcomes'][1]['price']
                    awayTeamOddsSite = sportsBook['title']
        odds['homeTeamOdds'] = homeTeamOdds
        odds['awayTeamOdds'] = awayTeamOdds
        odds['homeTeamOddsSite'] = homeTeamOddsSite
        odds['awayTeamOddsSite'] = awayTeamOddsSite
        odds['homeTeamBet'] = False
        odds['awayTeamBet'] = False
        odds['homeTeamId'] = game['homeTeamId']
        odds['awayTeamId'] = game['awayTeamId']
        homeOdds = 1/homeTeamOdds
        myOdds = game['prob']
        if myOdds + .2 < homeOdds  or myOdds  - .2 > homeOdds:
            continue
        if game['prob'] > 1/homeTeamOdds:
            odds['homeTeamBet'] = True
        if 1 - game['prob'] > 1/awayTeamOdds:
            odds['awayTeamBet'] = True
        if homeTeamOdds != 1 and awayTeamOdds != 1:
            bestOdds.append(odds)
    return bestOdds
    

@dailyOdds.route('/dailyOdds' , methods=['GET','POST'])
def daily_odds():
    #read the bookmakers.json file into a dictionary
    with open('./dailyOdds/bookmakers.json') as file:
        bookmakers = json.load(file)
    #get values of bookmakers dictionary and add to list
    bookMakerList = list(bookmakers.keys())
    bookMakerList.sort()
    if request.method == 'POST':
        selectedSportsBooks = request.form.getlist('bookMakers')
        keySelectedSportsBooks = set()
        for sportsBook in selectedSportsBooks:
            keySelectedSportsBooks.add(bookmakers[sportsBook])
        response = get_odds_oddsAPI()
        bestOdds = get_best_odds(response,keySelectedSportsBooks)
        return render_template('dailyOddsResult.html', bestOdds=bestOdds)
    return render_template('dailyOdds.html', bookMakerList=bookMakerList)
