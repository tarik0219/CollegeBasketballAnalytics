from flask import Blueprint, render_template
from utilscbb.espn import get_scores,get_espn_boxscore

boxscore = Blueprint('boxscore', __name__)


@boxscore.route('/boxscore/<gameId>/<date>')
def get_boxscore(gameId,date):
    scores = get_scores(date)
    score = scores[gameId]
    homeData, awayData = get_espn_boxscore(gameId)
    return render_template('boxscore.html', score=score, homeData=homeData, awayData=awayData)