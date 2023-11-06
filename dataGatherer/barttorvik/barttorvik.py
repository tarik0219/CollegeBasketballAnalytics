import bs4 as bs
import urllib.request
import json
import ssl
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
ssl._create_default_https_context = ssl._create_unverified_context


path = os.path.realpath(__file__)
dir = os.path.dirname(path)
bt_id_file = dir.replace('barttorvik', 'dicts') + '/bt_id.json'
with open(bt_id_file) as json_file:
    bt_id = json.load(json_file)

def get_url_bt(test,year):
    """
    Get Url if test == True use start and end date.
    """
    if test:
        return "https://barttorvik.com/trank.php?year={}&sort=&conlimit=#".format(year)
    else:
        return "https://barttorvik.com/trank.php?year={}&sort=&conlimit=#".format(year)

def get_table_rows_bt(test,year):
    """
    Return Rows of data.
    """
    url = get_url_bt(test,year)
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,"html.parser")
    table = soup.find('table')
    table_body = table.find('tbody')
    for br in soup.find_all("br"):
        br.replace_with("@")
    rows = table_body.find_all('tr')
    return rows

def change_team_names_bt(x):
    length = len(x.split('@'))
    if length > 1:
        return x.split('@')[0]
    else:
        return x

def get_dict_data_bt(test,year):
    rows = get_table_rows_bt(test,year)
    barttorvik = []
    for row in rows:
        try:
            send = {}
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            send = {
                    "name" : change_team_names_bt(cols[1]),
                    "rank": int(change_team_names_bt(cols[0])),
                    "offRating" : float(change_team_names_bt(cols[5])),
                    "defRating" : float(change_team_names_bt(cols[6])),
                    "TempoRating" : float(change_team_names_bt(cols[22]))
                }

            teamId = bt_id[change_team_names_bt(cols[1])]
            send['id'] = teamId
            barttorvik.append(send)
        except:
            print(send)
            pass
    return barttorvik

def UpdateBart():
    # container = connectToContainer("Teams")
    bartData = get_dict_data_bt(True,"2023")
    # for data in bartData:
    #     item = container.read_item(data, partition_key = data)
    #     item["barttorvik"] = bartData[data]
    #     print(item['teamName'])
    #     container.upsert_item(item)
    return bartData
    
if __name__ == "__main__":
    UpdateBart()
