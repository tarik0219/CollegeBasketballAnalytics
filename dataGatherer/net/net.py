import requests
from bs4 import BeautifulSoup
import requests
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilscbb import connectToContainer

path = os.path.realpath(__file__)
dir = os.path.dirname(path)
net_id_file = dir.replace('net', 'dicts') + '/net_id.json'
with open(net_id_file, 'r') as f:
    my_dict = json.load(f)

def net_rankings_to_dict():
    url = 'https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')
    
    # Extract column headers from first row
    headers = [header.text.strip() for header in rows[0].find_all('th')]

    # Extract data from remaining rows
    data = []
    for row in rows[1:]:
        values = [value.text.strip() for value in row.find_all('td')]
        data.append(dict(zip(headers, values)))
    
    netRank = {}
    for team in data:
        netRank[my_dict[team['School']]] = int(team['Rank'])
    return netRank

def update_net():
    container = connectToContainer("Teams")
    netData = net_rankings_to_dict()
    for data in netData:
        item = container.read_item(data, partition_key = data)
        item['net_rank'] = netData[data]
        print(item['teamName'])
        container.upsert_item(item)

if __name__ == "__main__":
    update_net()    
