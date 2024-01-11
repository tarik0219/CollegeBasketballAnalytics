import requests
import json
from utilscbb.constants import cbbAnalyticsApiUrl



def call_schedule_api(teamID,year,netRankBool):
    url = cbbAnalyticsApiUrl + "/teamSchedule"
    payload = json.dumps({"teamID": teamID, "year": year,"netRankBool": netRankBool})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response
