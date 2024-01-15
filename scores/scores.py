from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from constants.constants import CONF
from datetime import datetime
from wtforms import SelectField,SubmitField,validators
from wtforms.fields.html5 import DateField
import warnings
from utilscbb.api import get_scores
warnings.filterwarnings(action='ignore')


bs = Blueprint('scores', __name__)

class ScoreSearch(FlaskForm):
    games = SelectField('Search Games', choices = CONF)
    entrydate = DateField('Date', format='%Y-%m-%d', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')


def query_data(data, search):
    newData = []
    if search == "TOP 25":
        for value in data:
            home_rank = value.get('homeData', {}).get('ranks', {}).get('rank', 26)
            away_rank = value.get('awayData', {}).get('ranks', {}).get('rank', 26)
            if home_rank < 26 or away_rank < 26:
                newData.append(value)
        return newData
    elif search == "ALL":
        return data
    else:
        for value in data:
            home_conference = value.get('homeData', {}).get('conference')
            away_conference = value.get('awayData', {}).get('conference')
            if home_conference == search or away_conference == search:
                newData.append(value)
    return newData


def change_siteType(data):
    for count,game in enumerate(data):
        if game['siteType']:
            data[count]['siteType'] = "Yes"
        else:
            data[count]['siteType'] = "No"
    return data
    
@bs.route('/scores/<datesearch>/<search>' , methods=['GET','POST'])
def box_score(datesearch, search):
    entrydate = datetime.strptime(datesearch, '%Y-%m-%d')
    form = ScoreSearch(entrydate=entrydate, games=search)
    datesearch = datesearch.replace("-", "")
    if request.method == 'POST':
        search = request.form.get('games')
        datesearch = request.form.get('entrydate')
        session['datesearch'] = datesearch
        return redirect(url_for("scores.box_score", search=search, datesearch=datesearch))
    data = get_scores(datesearch)
    data = change_siteType(data)
    data = query_data(data, search)
    date = datesearch[4:6] + '/' + datesearch[6:8] + '/' + datesearch[0:4]
    data = sorted(data, key=lambda x: (2 if x['status'] == 'pre' else 1 if x['status'] == 'in' else 3, int(x['time'][:2])))
    return render_template('scores.html', data=data, form=form, date=date, search=search, datesearch=datesearch)
