from flask import Blueprint, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField,SubmitField,StringField,validators
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from utils.connectDB import connectDB

modelResults = Blueprint('modelResults', __name__)

class Search(FlaskForm):

    date = DateField('Date', format='%Y-%m-%d', default=datetime.today() - timedelta(days=1), validators=[validators.DataRequired()])


@modelResults.route('/results', methods=['GET','POST'])
def results():
    form = Search()
    if request.method == 'POST':
        if form.validate_on_submit():
            date = request.form.get('date').replace("-","")
            return redirect(url_for("modelResults.modelResultsPage", date = date))
    
    return render_template("results.html", form = form)


def calculate_projection_win(game):
    # 1==win,2==loss,3==draw
    if int(game['homeScore']) > int(game['awayScore']):
        if int(game['homeScorePredict']) > int(game['awayScorePredict']):
            return 1
        elif int(game['homeScorePredict']) < int(game['awayScorePredict']):
            return 2
        else:
            return 3
    elif int(game['homeScore']) < int(game['awayScore']):
        if int(game['homeScorePredict']) > int(game['awayScorePredict']):
            return 2
        elif int(game['homeScorePredict']) < int(game['awayScorePredict']):
            return 1
        else:
            return 3
    else:
        return 3

def calculate_over_under(game):
    score = int(game['homeScore']) + int(game['awayScore'])
    projectedScore = int(game['homeScorePredict']) + int(game['awayScorePredict'])
    if score == 0:
        return 3
    else:
        if score > game['overUnder']:
            if projectedScore > game['overUnder']:
                return 1
            elif projectedScore < game['overUnder']:
                return 2
            else:
                return 3
        elif score < game['overUnder']:
            if projectedScore > game['overUnder']:
                return 2
            elif projectedScore < game['overUnder']:
                return 1
            else:
                return 3
        else:
            return 3

def calculate_line(game):
    line = game['line'] * -1
    score = int(game['homeScore']) - int(game['awayScore'])
    projectedScore = int(game['homeScorePredict']) - int(game['awayScorePredict'])
    if score > line:
        if projectedScore > line:
            return 1
        elif projectedScore < line:
            return 2
        else:
            return 3
    elif score < line:
        if projectedScore > line:
            return 2
        elif projectedScore < line:
            return 1
        else:
            return 3
    else:
        return 3



def calculate_bet_stats(scores):
    records = {
        "projectionWin" : 0,
        "projectionLoss" : 0,
        "projectionDraw" : 0,
        "lineWin" : 0,
        "lineLoss" : 0,
        "lineDraw" : 0,
        "ouWin" : 0,
        "ouLoss" : 0,
        "ouDraw" : 0
    }
    for count,game in enumerate(scores):
        try:
            projection = calculate_projection_win(game)
            line = calculate_line(game)
            ou = calculate_over_under(game)
            if projection == 1:
                records['projectionWin'] += 1
                scores[count]['projection'] = projection
            elif projection == 2:
                records['projectionLoss'] += 1
                scores[count]['projection'] = projection
            else:
                records['projectionDraw'] += 1
                scores[count]['projection'] = projection
            
            if line == 1:
                records['lineWin'] += 1
                scores[count]['projectionLine'] = line
            elif line == 2:
                records['lineLoss'] += 1
                scores[count]['projectionLine'] = line
            else:
                records['lineDraw'] += 1
                scores[count]['projectionLine'] = line

            if ou == 1:
                records['ouWin'] += 1
                scores[count]['projectionOu'] = ou
            elif ou == 2:
                records['ouLoss'] += 1
                scores[count]['projectionOu'] = ou
            else:
                records['ouDraw'] += 1
                scores[count]['projectionOu'] = ou
        except:
            scores[count]['projectionOu'] = 3
            scores[count]['projectionLine'] = 3
            scores[count]['projection'] = 3
            records['ouDraw'] += 1
            records['lineDraw'] += 1
            records['projectionDraw'] += 1

    return records, scores

@modelResults.route('/results/<date>', methods=['GET','POST'])
def modelResultsPage(date):
    container = connectDB('boxscores')
    qry = f"SELECT * FROM c WHERE c.date = '{date}'"
    scores = list(container.query_items(qry, enable_cross_partition_query=True))
    records, scores = calculate_bet_stats(scores)
    date = date[:4] + '-' + date[4:6] + "-" + date[6:]
    return render_template("modelResults.html", scores = scores, records=records, date = date)