import pickle
import numpy as np
import os
import joblib
import os
import requests
from utilscbb.constants import cbbAnalyticsApiUrl
import json


def call_prediction_api(homeTeamData, awayTeamData, siteType):
    url = cbbAnalyticsApiUrl + "/predict"
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

def call_prediction_list_api(games):
    url = cbbAnalyticsApiUrl + "/predictList"
    payload = json.dumps(games)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response