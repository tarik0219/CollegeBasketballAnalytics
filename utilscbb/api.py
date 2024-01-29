from constants import constants
import requests
import json




def get_all_team_data():
    url = constants.CBB_AP_API_URL + "/teamData"
    response = requests.request("GET", url)
    return response.json()

def get_all_odds_by_date(date):
    url = constants.CBB_AP_API_URL + "/odds/date/" + date
    response = requests.request("GET", url)
    return response.json()

def get_team_data(teamId):
    url = constants.CBB_AP_API_URL + "/teamData/" + teamId
    response = requests.request("GET", url)
    return response.json()

def get_team_data_name(teamName):
    url = constants.CBB_AP_API_URL + "/teamData/teamName/" + teamName
    response = requests.request("GET", url)
    return response.json()

def get_conference_standings(conference):
    url = constants.CBB_AP_API_URL + "/getConferenceStandings/" + conference
    response = requests.request("GET", url)
    return response.json()

def get_scores(date):
    url = constants.CBB_AP_API_URL + "/scores/" + date
    response = requests.request("GET", url).json()
    return response['scores']

def get_prediction(homeTeamData, awayTeamData, siteType):
    url = constants.CBB_AP_API_URL + "/predict"
    payload = json.dumps({
        "homeData": homeTeamData['average'],
        "awayData": awayTeamData['average'],
        "neutralSite": siteType
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response['homeScore'],response['awayScore'],response['prob']

def get_prediction_list(games):
    url = constants.CBB_AP_API_URL + "/predictList"
    payload = json.dumps(games)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response

def get_schedule(teamID,year,netRankBool):
    url = constants.CBB_AP_API_URL + "/teamSchedule"
    payload = json.dumps({"teamID": teamID, "year": year,"netRankBool": netRankBool})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response

def get_odds_oddsAPI():
    url = constants.CBB_AP_API_URL + "/odds/oddsAPI"
    response = requests.request("GET", url)
    return response.json()


def get_bracketology_api():
    url = constants.CBB_AP_API_URL + "/bracketology"
    response = requests.request("GET", url)
    return response.json()


def get_seed_api():
    url = constants.CBB_AP_API_URL + "/seed"
    response = requests.request("GET", url)
    return response.json()