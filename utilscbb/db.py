from utilscbb.constants import cbbAnalyticsApiUrl
import requests



def get_all_team_data():
    url = cbbAnalyticsApiUrl + "/teamData"
    response = requests.request("GET", url)
    return response.json()


def get_team_data(teamId):
    url = cbbAnalyticsApiUrl + "/teamData/" + teamId
    response = requests.request("GET", url)
    return response.json()

def get_team_data_name(teamName):
    url = cbbAnalyticsApiUrl + "/teamData/teamName/" + teamName
    response = requests.request("GET", url)
    return response.json()

def get_db():
    return {}