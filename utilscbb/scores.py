
import numpy as np
import os
import requests
from utilscbb.constants import cbbAnalyticsApiUrl
import json


def call_scores_api(date):
    url = cbbAnalyticsApiUrl + "/scores/" + date
    response = requests.request("GET", url).json()
    return response['scores']