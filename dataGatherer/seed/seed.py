import pandas as pd # library for data analysis
import requests # library to handle requests
from bs4 import BeautifulSoup # library to parse HTML documents
import re
import pickle
from joblib import load

with open('conf_kp_sportsreference.pickle', 'rb') as f:
    conf_kp_sportsreference = pickle.load(f)

with open('id_kp.pkl', 'rb') as f:
    id_kp = pickle.load(f)
kp_id = {v: k for k, v in id_kp.items()}


def get_records_data():
    team_data = {}
    container = connectDB('records')
    data = container.read_all_items()
    for team in data:
        team_data[team['id']] = team
    return team_data

def conf_add(x):
    try:
        return conf_kp_sportsreference[x]
    except:
        return "MID"

def getKenpomWeb(url):
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.36'})
    data = page.text
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find('table', id="ratings-table")
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    return rows

def team_name(team):
    team  = re.sub(r'\d+', '', team)
    team = team.rstrip()
    return team

def add_records(kp):
    records = get_records_data()
    for index, row in kp.iterrows():
        team_data = records[row['id']]
        kp.loc[index, 'percent']  = team_data['projectedWin']/(team_data['projectedWin']+team_data['projectedLoss'])
        kp.loc[index, 'confW'] = team_data['confProjectedWin'] 
    return kp
    
def add_auto(kp):
    confs = list(kp['conference'].unique())
    champions = []
    for conf in confs:
        champion = list(kp[kp['conference'] == conf].sort_values(['confW', 'percent'], ascending = False)['Team'])[0]
        kp.loc[kp.Team == champion, 'auto'] = 1
    
    return kp

def conf_parse(conf):
    test = ['Big 12', 'Big Ten','SEC','Big East','ACC','Pac-12']
    if conf in test:
        return conf
    else:
        return "MID"

def GetKenpomData(url):
    rows = getKenpomWeb(url)
    kenpom = {}
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if len(cols) == 0:
            pass
        else:
            kenpomRank = int(cols[0])
            kenpomTeamName = team_name(cols[1])
            kenpomConf = cols[2]
            kenpomW = int(cols[3].split("-")[0])
            kenpomL = int(cols[3].split("-")[1])
            kenpomOff = float(cols[5])
            kenpomDef = float(cols[7])
            kenpomTempo = float(cols[9])
            kenpomSos = int(cols[14])

            send = {
                "Team" : kenpomTeamName,
                "rank": kenpomRank,
                "conference" : kenpomConf,
                "w":kenpomW,
                "l":kenpomL,
                "offRating" : kenpomOff,
                "defRating" : kenpomDef,
                "TempoRating" : kenpomTempo,
                "sos":kenpomSos
            }
        kenpom[kenpomTeamName] = send
    kp = pd.DataFrame.from_dict(kenpom, orient='index',columns=['Team','rank', 'conference', 'w','l','offRating', 'defRating','TempoRating','sos']).reset_index(drop=True)
    kp['id']  = kp['Team'].apply(lambda x: kp_id[x])
    kp['percent'] = 0.0
    kp['confW'] = 0
    kp['auto'] = 0
    kp = add_records(kp)
    kp = add_auto(kp)
    kp['conference']  = kp['conference'].apply(lambda x: conf_add(x))
    kp['conference']  = kp['conference'].apply(lambda x: conf_parse(x))
    return kp

def calculate_at_large():
    df = GetKenpomData("https://kenpom.com/")
    model = load("at_large.joblib")
    at_large = df
    one_hot = pd.get_dummies(at_large['conference'])
    at_large = at_large.drop('conference',axis = 1)
    at_large = at_large.join(one_hot)
    X = at_large[['offRating', 'defRating', 'sos','percent']]
    at_large['at_large_prob'] = model.predict_proba(X)[:, 1] * 100

    at_large_teams = list(at_large[at_large['auto'] == 0].sort_values(['at_large_prob'], ascending = False)['Team'])[:36]
    last_four_teams = list(at_large[at_large['auto'] == 0].sort_values(['at_large_prob'], ascending = False)['Team'])[32:36]
    at_large['at_large'] = at_large['Team'].apply(lambda x: 1 if x in at_large_teams else 0)
    at_large['in'] = at_large.apply(lambda x: 1 if x['auto'] == 1 or x['at_large'] == 1 else 0, axis = 1)
    at_large['last_4_in'] = at_large['Team'].apply(lambda x: 1 if x in last_four_teams else 0 )
    at_large['first_4_out'] = at_large['Team'].apply(lambda x: 1 if x in list(at_large[at_large['auto'] == 0].sort_values(['at_large_prob'], ascending = False)['Team'])[36:40] else 0 )
    at_large['next_4_out'] = at_large['Team'].apply(lambda x: 1 if x in list(at_large[at_large['auto'] == 0].sort_values(['at_large_prob'], ascending = False)['Team'])[40:44] else 0 )
    field_of_68 = at_large[at_large['in'] == 1]
    model = load("seed.joblib")
    X = field_of_68[['offRating', 'defRating', 'sos','percent']]
    field_of_68['projected_seed'] = model.predict(X)
    field_of_68 = field_of_68.sort_values(['projected_seed','at_large_prob'], ascending = [True,False])
    non_last_four_at_large = at_large_teams[:-4]
    field_of_68['seed'] = 0



    count = 0
    seed = 1
    last_four = 0
    last_four_seed = 0
    last_four_teams
    non_last_four_at_large
    teams = []
    test = False
    for index, row in field_of_68.iterrows():
        if len(non_last_four_at_large) == 0 and test == False:
            for team in teams:
                if last_four == 1:
                    field_of_68.loc[df.Team == team, 'seed'] = last_four_seed
                    last_four = 0
                elif last_four == 0:
                    last_four_seed = seed
                    field_of_68.loc[df.Team == team, 'seed'] = seed
                    count += 1
                    last_four += 1
                if count == 4:
                    count = 0
                    seed+=1
                if seed > 16:
                    seed = 16
            test = True
        if row['Team'] in non_last_four_at_large:
            non_last_four_at_large.remove(row['Team'])
        if row['Team'] in last_four_teams and len(non_last_four_at_large) != 0:
            teams.append(row['Team']) 
        elif row['Team'] in last_four_teams and test == True:
            if last_four == 1:
                field_of_68.loc[index, 'seed'] = last_four_seed
                last_four = 0
            elif last_four == 0:
                last_four_seed = seed
                field_of_68.loc[index, 'seed'] = seed
                count += 1
                last_four += 1
        else:
            field_of_68.loc[index, 'seed'] = seed
            count+=1
        if count == 4:
            count = 0
            seed+=1
        if seed > 16:
            seed = 16
    field_of_68['play_in'] = field_of_68['Team'].apply(lambda x: 1 if x in list(field_of_68.sort_values(['projected_seed', 'rank'], ascending = True)[-4:]['Team']) else 0)
    df = at_large.merge(field_of_68[['Team','seed','play_in']], how='left', on = "Team")
    df = df[['Team','sos', 'id', 'auto','at_large_prob', 'at_large', 'in',
        'last_4_in', 'first_4_out', 'next_4_out','play_in','seed']]
    df = df.fillna(17)
    df['seed'] = df['seed'].apply(lambda x: int(x))
    return df

def get_team_data():
    team_data = {}
    container = connectDB('Teams')
    data = container.read_all_items()
    for team in data:
        team_data[team['id']] = team['teamName']
    return team_data

def add_to_db(df):
    teams = get_team_data()
    df['Team'] = df['id'].apply(lambda x: teams[x])
    container = connectDB('seed')
    for index, row in df.iterrows():
        send = {}
        for item in list(df.columns):
            send[item] = row[item]
        try:
            container.upsert_item(send)
        except:
            container.create_item(send)

if __name__ == "__main__":
    df = calculate_at_large()
    add_to_db(df)