from flask import Blueprint, render_template
from tinydb import TinyDB, Query
from tinydb.operations import set
from utilscbb.db import get_db

conference = Blueprint('conference', __name__)


def get_teams(conf,query,teamsTable):
    team_data = teamsTable.search(query.conference == conf)
    return team_data

def get_all_conf_data(query,teamsTable):
    teams = teamsTable.all()
    conf_data = {}
    for item in teams:
        if item['conference'] in conf_data:
            conf_data[item['conference']]['count'] += 1
            conf_data[item['conference']]['rank'] += item['ranks']['rank']
            conf_data[item['conference']]['average'] = conf_data[item['conference']]['rank']/conf_data[item['conference']]['count']
            if conf_data[item['conference']]['max'] < item['ranks']['rank']:
                conf_data[item['conference']]['max'] = item['ranks']['rank']
            if conf_data[item['conference']]['min'] > item['ranks']['rank']:
                conf_data[item['conference']]['min'] = item['ranks']['rank']
        else:
            conf_data[item['conference']] ={
                "count":1,
                "rank":item['ranks']['rank'],
                "average":item['ranks']['rank'],
                "max":item['ranks']['rank'],
                "min":item['ranks']['rank'],
            }
    data = []
    for key,item in conf_data.items():
        item['conference'] = key
        data.append(item)
    return data


@conference.route('/conference/<conf>')
def conference_stadnings(conf):
    query,teamsTable = get_db()
    data = get_teams(conf,query,teamsTable)
    data.sort(key=lambda x: (x["record"]['confProjectedWin'],x["record"]['confWin']), reverse=True)
    return render_template('conference.html', data=data, conference = conf)

@conference.route('/conference')
def conference_rank():
    query,teamsTable = get_db()
    data = get_all_conf_data(query,teamsTable)
    data.sort(key=lambda x: x["average"], reverse=False)
    return render_template('conferenceRanks.html', data=data)
