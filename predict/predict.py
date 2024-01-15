from flask import Blueprint, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField
from utilscbb.api import get_all_team_data, get_team_data_name
import random
from werkzeug.datastructures import MultiDict
from utilscbb.api import get_prediction



predict = Blueprint('predict', __name__)

class PredictGame(FlaskForm):
    data = get_all_team_data()
    teams = []
    for team in data:
        teams.append(team['teamName'])
    hometeam = SelectField('Home Team', choices = teams)
    awayteam = SelectField('Away Team', choices = teams)
    neutral = SelectField('Neutral Venue', choices = ['No','Yes'])

@predict.route('/predict',methods=['GET','POST'])
def predict_game():
    if request.method == 'GET':
        form = PredictGame(formdata=MultiDict({'hometeam': random.choice(PredictGame.teams), 'awayteam': random.choice(PredictGame.teams)}))
    else:
        form = PredictGame()
    if request.method == 'POST':
        if form.validate_on_submit():
            hometeam = request.form.get('hometeam')
            awayteam = request.form.get('awayteam')
            neutral = request.form.get('neutral')
            return redirect(url_for("predict.predictresults", hometeam = hometeam, awayteam=awayteam, neutral = neutral))
    return render_template("predict.html", form = form)



@predict.route('/predict/<hometeam>/<awayteam>/<neutral>', methods=['GET'])
def predictresults(hometeam,awayteam,neutral):
    if neutral == "Yes":
        neutral = True
    else:
        neutral = False
    homeData = get_team_data_name(hometeam)
    awayData = get_team_data_name(awayteam)
    homeScore,awayScore,prob = get_prediction(homeData,awayData,neutral)
    prob = prob * 100
    return render_template("predictResults.html", homeData = homeData, awayData = awayData, homeScore = homeScore, awayScore = awayScore, prob = prob)


