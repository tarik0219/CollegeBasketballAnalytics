from flask import Blueprint, render_template, request
from utilscbb.api import get_bracketology_api,get_all_team_data, get_seed_api
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
    seedData = get_seed_api()
    confereceDict = {}
    for team in seedData:
        conference = teamDict[team[1]]['conference']
        if conference not in confereceDict:
            confereceDict[conference] = {}
            confereceDict[conference]['bids'] = 1
            confereceDict[conference]['teams'] = [teamDict[team[1]]['id']]
        else:
            confereceDict[conference]['bids'] += 1
            teams = confereceDict[conference]['teams']
            teams.append(teamDict[team[1]]['id'])
            confereceDict[conference]['teams'] = teams
    conferenceList = []
    for key,value in confereceDict.items():
        conferenceList.append([key,value['bids']])
    conferenceList.sort(key=lambda x: x[1], reverse=True)
    return render_template('bracketology.html', bracketology=bracketology, teamDict=teamDict, seedData=seedData, conferenceList=conferenceList, confereceDict=confereceDict)