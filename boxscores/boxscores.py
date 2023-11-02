from flask import Blueprint, render_template
from utils.connectDB import connectDB
from utils.espn import get_scores,get_espn_boxscore

boxscore = Blueprint('boxscore', __name__)

def get_azure_boxscore(gameId):
    container = connectDB('boxscores')
    qry = f"SELECT * FROM c WHERE c.id = '{gameId}'"
    scores = list(container.query_items(qry, enable_cross_partition_query=True))
    if len(scores) == 0:
        return {}
    else:
        return scores[0]




@boxscore.route('/boxscore/<gameId>/<date>')
def get_boxscore(gameId,date):
    scores = get_scores(date)
    score = scores[gameId]
    homeData, awayData = get_espn_boxscore(gameId)
    azure = get_azure_boxscore(gameId)
    return render_template('boxscore.html', score=score, homeData=homeData, awayData=awayData, azure=azure)