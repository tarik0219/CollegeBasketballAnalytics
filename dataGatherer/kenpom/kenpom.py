#from azure.cosmos import exceptions, CosmosClient, PartitionKey
from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
import pickle
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

path = os.path.realpath(__file__)
dir = os.path.dirname(path)
id_kp_file = dir.replace('kenpom', 'dicts') + '/id_kp.pkl'
with open(id_kp_file, 'rb') as f:
    id_kp = pickle.load(f)

conf_kp_sportsreference_file = dir.replace('kenpom', 'dicts') + '/conf_kp_sportsreference.pickle'
with open(conf_kp_sportsreference_file, 'rb') as f:
    conf_kp_sportsreference = pickle.load(f)

def team_name(team):
    team  = re.sub(r'\d+', '', team)
    team = team.rstrip()
    return team

def getKenpomWeb():
    url = "https://kenpom.com"
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.36'})
    data = page.text
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find('table', id="ratings-table")
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    return rows

def GetKenpomData(kp_id):
    rows = getKenpomWeb()
    kenpom = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if len(cols) == 0:
            pass
        else:
            kenpomRank = int(cols[0])
            kenpomTeamName = team_name(cols[1])
            kenpomConf = cols[2]
            kenpomOff = float(cols[5])
            kenpomDef = float(cols[7])
            kenpomTempo = float(cols[9])

            send = {
                "name" : kenpomTeamName,
                "rank": kenpomRank,
                "conference" : kenpomConf,
                "offRating" : kenpomOff,
                "defRating" : kenpomDef,
                "TempoRating" : kenpomTempo,
            }
            try:
                teamId = kp_id[kenpomTeamName]
                send['id'] = teamId
                kenpom.append(send)
            except:
                print(send)
                pass
            
    return kenpom

def UpdateKenpom():
    #container = connectToContainer("Teams")
    kenpomData = GetKenpomData({v: k for k, v in id_kp.items()})
    # for data in kenpomData:
    #     item = container.read_item(data, partition_key = data)
    #     conference = conf_kp_sportsreference[kenpomData[data]['conference']]
    #     item["kenpom"] = kenpomData[data]
    #     item['conference'] = conference
    #     container.upsert_item(item)

    return kenpomData

if __name__ == "__main__":
    print('Starting to Get Kenpom Data')
    UpdateKenpom()
    print('Finished gettting Kenpom Data')

