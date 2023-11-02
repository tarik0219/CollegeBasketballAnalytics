from flask import Blueprint, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField,SubmitField,StringField,validators
from utils.connectDB import connectDB
import random
from werkzeug.datastructures import MultiDict
from utils.predict import make_prediction




history = Blueprint('history', __name__)

class PredictGame(FlaskForm):
    container = connectDB('history')
    data = list(container.read_all_items())
    teams = []
    for team in data:
        if team not in teams:
            teams.append(team['name'])
    teams = [*set(teams)]
    teams = sorted(teams)
    hometeam = SelectField('Home Team', choices = teams)
    homeYear = SelectField('Home Year', choices = [*range(2002, 2023, 1)], validators=[validators.DataRequired()])
    awayteam = SelectField('Away Team', choices = teams)
    awayYear = SelectField('Away Year', choices = [*range(2002, 2023, 1)], validators=[validators.DataRequired()])
    neutral = SelectField('Neutral Venue', choices = ['No','Yes'])

    def validate(self):
        container = connectDB('history')
        espn_id = get_espn_id()
        result = True
        try:
            id = espn_id[self.hometeam.data]+str(self.homeYear.data)
            response = container.read_item(item=id, partition_key=id)
        except:
            self.homeYear.errors = list(self.homeYear.errors )
            self.homeYear.errors.append('Team has no Data for that year!')
            result = False
        try:
            id = espn_id[self.awayteam.data]+str(self.awayYear.data)
            response = container.read_item(item=id, partition_key=id)
        except:
            self.awayYear.errors = list(self.awayYear.errors)
            self.awayYear.errors.append('Team has no Data for that year!')
            result = False
        return result


def get_espn_id():
    container = connectDB('Teams')
    data = list(container.read_all_items())
    espn_id = {}
    for team in data:
        espn_id[team["teamName"]] = team['id']
    return espn_id

def get_team_data(team,year,espn_id):
    container = connectDB('history')
    id = espn_id[team]+str(year)
    response = container.read_item(item=id, partition_key=id)
    return response

@history.route('/historical', methods=['GET','POST'])
def history_predict():
    if request.method == 'GET':
        form = PredictGame(formdata=MultiDict({'hometeam': random.choice(PredictGame.teams), 'awayteam': random.choice(PredictGame.teams), "homeYear":random.choice([*range(2002, 2023, 1)]), "awayYear":random.choice([*range(2002, 2023, 1)]), "neutral":random.choice(["No","Yes"])}))
    else:
        form = PredictGame()
    if request.method == 'POST':
        if form.validate_on_submit():
            hometeam = request.form.get('hometeam')
            awayteam = request.form.get('awayteam')
            homeYear = request.form.get('homeYear')
            awayYear = request.form.get('awayYear')
            neutral = request.form.get('neutral')
            return redirect(url_for("history.history_predict_results", hometeam = hometeam, awayteam=awayteam, neutral = neutral, homeYear=homeYear,awayYear=awayYear))
    return render_template("predictHistory.html", form = form)


@history.route('/historical/<hometeam>/<homeYear>/<awayteam>/<awayYear>/<neutral>', methods=['GET'])
def history_predict_results(hometeam,homeYear,awayteam,awayYear,neutral):
    if neutral == "Yes":
        neutral = True
    else:
        neutral = False
    espn_id = get_espn_id()
    homeData = get_team_data(hometeam,homeYear,espn_id)
    homeData = {'average':homeData['kenpom'], 'name': homeData['name']}
    awayData = get_team_data(awayteam,awayYear,espn_id)
    awayData = {'average':awayData['kenpom'], 'name': awayData['name']}
    homeScore,awayScore,prob = make_prediction(homeData,awayData,neutral)
    prob = prob * 100
    return render_template("predictHistoryResults.html", homeData = homeData, awayData = awayData, homeScore = homeScore, awayScore = awayScore, prob = prob, homeYear = homeYear, awayYear=awayYear)

