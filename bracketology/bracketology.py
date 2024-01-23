from flask import Blueprint, render_template, request
from utilscbb.api import get_bracketology_api,get_all_team_data
import json

bracket = Blueprint('bracket', __name__)

def teams_to_dict(teams):
    team_dict = {}
    for team in teams:
        team_dict[team['teamName']] = team
    return team_dict

@bracket.route('/bracketology' , methods=['GET','POST'])
def get_bracketology():
    bracketology = get_bracketology_api()
    allTeamData = get_all_team_data()
    teamDict = teams_to_dict(allTeamData)
    return render_template('bracketology.html', bracketology=bracketology, teamDict=teamDict)