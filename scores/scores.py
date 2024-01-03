from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from utilscbb.espn import get_scores, get_line_data
from utilscbb.constants import CONF
from datetime import datetime
from wtforms import SelectField,SubmitField,validators
from wtforms.fields.html5 import DateField
from utilscbb.predict import call_prediction_api, call_prediction_list_api
import warnings
from utilscbb.db import get_all_team_data
from utilscbb.constants import dbFileName
from utilscbb.cahce import get_cache
import requests
import json
from utilscbb.cahce import get_cache
warnings.filterwarnings(action='ignore')


bs = Blueprint('scores', __name__)

class ScoreSearch(FlaskForm):
    games = SelectField('Search Games', choices = CONF)
    entrydate = DateField('Date', format='%Y-%m-%d', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')


def add_info(data):
    teamData = {}
    for team in get_all_team_data():
        teamData[team['id']] = team
    for gameId,value in data.items():
        data[gameId]['homeData'] = teamData[value['homeTeamId'] ] if value['homeTeamId'] in teamData else None
        data[gameId]['awayData'] = teamData[value['awayTeamId'] ] if value['awayTeamId'] in teamData else None
    return data


def add_prediction(data):
    requestData = []
    for gameId,value in data.items():
        if data[gameId]['homeData'] and data[gameId]['awayData']: 
            requestData.append({
                "homeData": data[gameId]['homeData']['average'],
                "awayData": data[gameId]['awayData']['average'],
                "neutralSite": data[gameId]['siteType']
            })
        else:
            pass
    response = call_prediction_list_api({"games":requestData})
    count = 0
    for gameId,value in data.items():
        if data[gameId]['homeData'] and data[gameId]['awayData']: 
            data[gameId]['homeScorePredict'] = response[count]['homeScore']
            data[gameId]['awayScorePredict'] =  response[count]['awayScore']
            data[gameId]['prob'] = response[count]['prob']
            count += 1
        else:
            data[gameId]['homeScorePredict'] = None   
            data[gameId]['awayScorePredict'] = None
            data[gameId]['prob'] = None
    return data

def query_data(data,search):
    new_data = {}
    if search == "TOP 25":
        for gameId,value in data.items():
            try:
                if value['homeData']['ranks']['rank'] <= 25:
                    new_data[gameId] = value
                    continue
            except:
                pass
            try:
                if value['awayData']['ranks']['rank'] <= 25:
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

def add_line_data(data):
    for i, gameId in enumerate(data):
        response = get_line_data(gameId)
        if len(response['items']) == 0:
            continue
        else:
            line = response['items'][0].get('spread')
            overUnder = response['items'][0].get('overUnder')
            data[gameId]["line"] = line
            data[gameId]["overUnder"] = overUnder
    return data

def get_line_data(gameId):
    query, cache = get_cache()
    cacheResponse = cache.search(query.gameId == gameId)
    if len(cacheResponse) != 0:
        return json.loads(cacheResponse[0]["response"])
    url = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/{}/competitions/{}/odds?=".format(gameId, gameId)
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
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
    data = add_prediction(data)
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
    for key,value in data[0].items():
        print(key)
    return render_template('scores.html', data = data, form = form, date = date, search = search, datesearch = datesearch)