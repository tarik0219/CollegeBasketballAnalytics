from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from utilscbb.espn import get_scores, convertDateTime, get_line_data
from utilscbb.constants import CONF
from datetime import datetime
from datetime import timedelta
from wtforms import SelectField,SubmitField,StringField,validators
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from pytz import timezone
import pickle
import numpy as np
from werkzeug.datastructures import MultiDict
from utilscbb.predict import make_prediction
import warnings
from utilscbb.db import get_db
from utilscbb.cahce import get_cache
import concurrent.futures
import threading
import requests
import json
from tinydb import TinyDB, Query
from tinydb.operations import set
import os
from utilscbb.cahce import get_cache
warnings.filterwarnings(action='ignore')


bs = Blueprint('scores', __name__)

class ScoreSearch(FlaskForm):
    games = SelectField('Search Games', choices = CONF)
    entrydate = DateField('Date', format='%Y-%m-%d', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')


def add_info(data):
    query, teamsTable = get_db()
    teams = teamsTable.all()
    team_data = {}
    for item in teams:
        team_data[item['id']] = item

    for gameId,value in data.items():
        if value['homeTeamId'] in team_data and value['awayTeamId'] in team_data:
            data[gameId]['homeData'] = team_data[value['homeTeamId']]
            data[gameId]['awayData'] = team_data[value['awayTeamId']]
        else:
            data[gameId]['homeData'] = None
            data[gameId]['awayData'] = None
    return data


def add_prediction(data,date):
    for gameId,value in data.items():
        if data[gameId]['homeData'] != None and data[gameId]['awayData'] != None and datetime.now().date() < datetime.strptime(date, '%Y%m%d').date(): 
            home, away, prob = make_prediction(data[gameId]['homeData'], data[gameId]['awayData'], data[gameId]['siteType'])
            data[gameId]['homeScorePredict'] = home
            data[gameId]['awayScorePredict'] = away
            data[gameId]['prob'] = prob
        else:
            data[gameId]['homeScorePredict'] = None   
            data[gameId]['awayScorePredict'] = None
            data[gameId]['prob'] = None
    return data

def query_data(data,search):
    new_data = {}
    if search == "TOP 25":
        for gameId,value in data.items():
            print(value)
            try:
                if value['homeData']['ranks']['rank'] <= 25:
                    new_data[gameId] = value
                    continue
            except:
                pass
            try:
                if value['homeData']['ranks']['rank'] <= 25:
                    new_data[gameId] = value
            except:
                pass
    elif search == "ALL":
        return data
    else:
        for gameId,value in data.items():
            try:
                if value['homeData']['conference'] == search:
                    new_data[gameId] = value
                    continue
            except:
                pass
            try:
                if value['awayData']['conference'] == search:
                    new_data[gameId] = value
            except:
                pass
    return new_data

def add_sort(data):
    for count,game in enumerate(data):
        if game['status'] == 'pre':
            data[count]['sort1'] = 2
        elif game['status'] == 'in':
            data[count]['sort1'] = 1
        else:
            data[count]['sort1'] = 3
        
        data[count]['sort2'] = int(game['time'][:2])
    return data

def change_siteType(data):
    for count,game in enumerate(data):
        if game['siteType']:
            data[count]['siteType'] = "Yes"
        else:
            data[count]['siteType'] = "No"
    return data


# file_lock = threading.Lock()
cache_lock = threading.Lock()
def add_line_data(data):
    num_threads = 10  # You can change this to the desired number of parallel threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for gameId in data:
            future = executor.submit(get_line_data, gameId)
            futures.append(future)

    for i, gameId in enumerate(data):
        response = futures[i].result()

        if len(response['items']) == 0:
            continue
        else:
            line = response['items'][0].get('spread')
            overUnder = response['items'][0].get('overUnder')
            data[gameId]["line"] = line
            data[gameId]["overUnder"] = overUnder
    return data

def get_line_data(gameId):
    with cache_lock:
        query, cache = get_cache()
        cacheResponse = cache.search(query.gameId == gameId)
        if len(cacheResponse) != 0:
            print("Cache hit for gameId:", gameId)
            return json.loads(cacheResponse[0]["response"])
    url = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/{}/competitions/{}/odds?=".format(gameId, gameId)
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    with cache_lock:
        cache.insert(
            {
                "gameId": gameId,
                "response": json.dumps(response.json())
            }
        )
    return response.json()



@bs.route('/scores/<datesearch>/<search>' , methods=['GET','POST'])
def box_score(datesearch,search):
    entrydate = datetime.strptime(datesearch, '%Y-%m-%d')
    form = ScoreSearch(entrydate=entrydate, games = search)
    datesearch = datesearch.replace("-", "")
    if request.method == 'POST':
        search = request.form.get('games')
        datesearch = request.form.get('entrydate')
        session['datesearch'] = datesearch
        return redirect(url_for("scores.box_score", search = search, datesearch = datesearch))
    data = get_scores(datesearch)
    data = add_info(data)
    data = query_data(data,search)
    data = add_prediction(data,datesearch)
    data = add_line_data(data)
    date = datesearch[4:6]+'/'+datesearch[6:8]+'/'+datesearch[0:4] 
    send = []
    for key,value in data.items():
        value['id'] = key
        send.append(value)
    data = send
    data = add_sort(data)
    data = change_siteType(data)
    data = sorted(data, key=lambda x: (x['sort1'], x['sort2']) )
    return render_template('scores.html', data = data, form = form, date = date, search = search, datesearch = datesearch)