from typing import ItemsView
import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tinydb import TinyDB, Query
from tinydb.operations import set


def calc_average(stat, statNames, data):
    sum = 0
    count = 0
    for name in statNames:
        sum += data[name][stat]
        count += 1
    return sum/count

def addAverage(query,teamsTable):
    data = teamsTable.all()
    for team in data:
        team['average'] = {
            "offRating":calc_average('offRating', ["barttorvik","kenpom"], team),
            "defRating":calc_average('defRating', ["barttorvik","kenpom"], team),
            "TempoRating":calc_average('TempoRating', ["barttorvik","kenpom"], team),
        }
        team['ranks'] = {
            'stat_rank': None,
            "rank": None,
            "rankOff": None,
            "rankDef": None,
            "rankTempo": None
        }
        teamsTable.upsert(team, query.id == team['id'])

def addStatRank(query,teamsTable):
    data = teamsTable.all()
    data.sort(key=lambda x: x["barttorvik"]["offRating"] - x["barttorvik"]["defRating"] + x["kenpom"]["offRating"] - x["barttorvik"]["defRating"], reverse=True)
    for count,team in enumerate(data):
        team['ranks']['stat_rank'] = count + 1
        teamsTable.upsert(team, query.id == team['id'])

# def addApRank():
#     url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/rankings"
#     payload={}
#     headers = {}
#     response = requests.request("GET", url, headers=headers, data=payload)

#     ranks = response.json()['rankings'][0]['ranks']
#     others = response.json()['rankings'][0]['others']

#     ap_ranks = {}
#     for count,team in enumerate(ranks):
#         ap_ranks[team['team']['id']] = count + 1
        
#     for count,team in enumerate(others):
#         ap_ranks[team['team']['id']] = count + 26

#     container = connectToContainer('Teams')
#     data = list(container.read_all_items())
#     length_rank = len(ap_ranks)
#     for count,team in enumerate(data):
#         if team['id'] in ap_ranks:
#             team['ranks']['ap_rank'] = ap_ranks[team['id']]
#         else:
#             if team['stat_rank'] < length_rank:
#                 team['ranks']['ap_rank'] = length_rank + 1
#             else:
#                 team['ranks']['ap_rank'] = team['stat_rank']
#         container.upsert_item(team)

def addRank(query,teamsTable):
    data = teamsTable.all()
    data.sort(key=lambda x: x['ranks']["stat_rank"], reverse=False)
    #data.sort(key=lambda x: x["stat_rank"] + x["ap_rank"], reverse=False)
    for count,team in enumerate(data):
        team['ranks']['rank'] = count + 1
        teamsTable.upsert(team, query.id == team['id'])

def addOff(query,teamsTable):
    data = teamsTable.all()
    data.sort(key=lambda x: x["barttorvik"]["offRating"]  + x["kenpom"]["offRating"] , reverse=True)
    for count,team in enumerate(data):
        team['ranks']['rankOff'] = count + 1
        teamsTable.upsert(team, query.id == team['id'])

def addDef(query,teamsTable):
    data = teamsTable.all()
    data.sort(key=lambda x: x["barttorvik"]["defRating"]  + x["kenpom"]["defRating"] , reverse=False)
    for count,team in enumerate(data):
        team['ranks']['rankDef'] = count + 1
        teamsTable.upsert(team, query.id == team['id'])

def addTempo(query,teamsTable):
    data = teamsTable.all()
    data.sort(key=lambda x: x["barttorvik"]["TempoRating"]  + x["kenpom"]["TempoRating"] , reverse=True)
    for count,team in enumerate(data):
        team['ranks']['rankTempo'] = count + 1
        teamsTable.upsert(team, query.id == team['id'])

def updateStats(query,teamsTable):
    print('Calculating Average')
    addAverage(query,teamsTable)
    print('Calculating Stats Rank')
    addStatRank(query,teamsTable)
    # print('Calculating AP Rank')
    # addApRank()
    print('Calculating Average Rank')
    addRank(query,teamsTable)
    print('Calculating OFF Rank')
    addOff(query,teamsTable)
    print('Calculating DEF Rank')
    addDef(query,teamsTable)
    print('Calculating TEMPO Rank')
    addTempo(query,teamsTable)
    print('Done Caclculating')