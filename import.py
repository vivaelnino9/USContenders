import json
import inspect
from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4 import NavigableString
from collections import OrderedDict


SERVER_CHOICES = [
"Radius","Pi","Origin","Sphere","Centra","Orbit","Chord","Diameter","Any"
]

POSITION_CHOICES = ["O","D","O/D","D/O"]

lst = ['B','C', 'D', 'E', 'F', 'G', 'H', 'I',]
# to help specify what columns in spreadsheet to scrape through


players = []

def make_data():
    data = make_players()
    with open('data.json', 'w') as outfile:
            json.dump(data, outfile)
    print('completed')
def make_players():
    sheet = 'https://docs.google.com/spreadsheets/d/13-nO0zc-EzStByOFnXJhwzHNhl4NHSnHvz54DJpdcNw'
    page = urlopen(sheet)
    soup = BeautifulSoup(page,'lxml')
    cols = [header.string for header in soup.find('thead').findAll('th')]
    players_data = []
    for c in cols:
        if c in lst:
            col_values = [td[cols.index(c)].string
                      for td in [tr.findAll('td')
                                 for tr in soup.find('tbody').findAll('tr')]]
            for player in col_values[1:]:
                if player is not None and player not in players:
                    players.append(str(player))
    pk = 1
    for player in players:
        players_data.append(make_user(player,pk))
        pk += 1
    pk = 1
    for player in players:
        p = OrderedDict()
        p['pk'] = pk
        p['model'] = 'usc_app.Player'
        p['fields'] = OrderedDict()
        p['fields']['user'] = pk
        p['fields']['name'] = player
        p['fields']['minutes'] = 0
        p['fields']['tags'] = 0
        p['fields']['captures'] = 0
        p['fields']['hold'] = 0
        p['fields']['returns'] = 0
        players_data.append(p)
        pk += 1
    return make_rosters(players,players_data,soup)


def make_captains(captains,rosters_data):
    captains_data = []
    for captain,values in captains.items():
        c = OrderedDict()
        c['pk'] = values['user_pk']
        c['model'] = 'usc_app.Captain'
        c['fields'] = OrderedDict()
        # c['fields']['user'] = values['user_pk']
        c['fields']['team'] = values['team_pk']
        captains_data.append(c)

    captains_data += rosters_data
    return captains_data
def make_rosters(players,players_data,soup):
    rows = soup.find_all('tr')
    avoid = [None,'Logo','Intro','Skin']

    rosters = OrderedDict()

    for row in rows[2:]:
        cells = row.find_all('td')
        if len(cells) == 16:
            avoid.append(cells[0].string)
            rosters[cells[0].string] = [cell.string for cell in cells if cell.string not in avoid]

    rosters_data = []
    captains = {}
    for roster,values in rosters.items():
        r = OrderedDict()
        roster_pk = (list(rosters.keys()).index(roster))+1
        r['pk'] = roster_pk
        r['model'] = 'usc_app.Roster'
        r['fields'] = OrderedDict()
        r['fields']['team_name'] = roster
        r['fields']['rank'] = 0
        r['fields']['abv'] = 'temp'

        for value in values:
            if value in players:
                position = assign_player(r)
                index = players.index(value)
                user_pk = index+1
                players_data[index]['fields']['team'] = roster
                if position == 'captain':
                    captains[value] = {'user_pk':user_pk,'team_pk':roster_pk}
                r['fields'][position]= user_pk
            else:
                try:
                    int(value)
                    r['fields']['daysActive'] = int(value)
                except ValueError:
                    if value in SERVER_CHOICES:
                        r['fields']['server'] = (SERVER_CHOICES.index(value))+1
                    else:
                        if value == '#N/A':
                            pass
                        else:
                            date = value.split('/')
                            fixed_date = date[2]+'-'+date[0]+'-'+date[1]
                            r['fields']['firstActive'] = fixed_date
        rosters_data.append(r)
    rosters_data += players_data
    rosters_data += make_stats(rosters,rosters_data)
    return make_captains(captains,rosters_data)

def make_stats(rosters,rosters_data):
    sheet = 'https://docs.google.com/spreadsheets/d/1qSSKoql8frQ3VNyVY9XIV-KbLLv0QnpE_T8zunQF-jQ'
    page = urlopen(sheet)
    soup = BeautifulSoup(page,'lxml')
    rows = soup.find_all('tr')
    avoid = [None,]

    stats_data = []
    for row in rows[4:-2]:
        cells = row.find_all('td')
        if len(cells) == 21 and cells[2].string is not None or len(cells) == 20 and cells[1].string is not None:
            s = OrderedDict()
            pk = list(rosters.keys()).index(cells[4].string) if len(cells) == 21 else list(rosters.keys()).index(cells[3].string)
            s['pk'] = pk+1
            s['model'] = 'usc_app.Stats'
            s['fields'] = OrderedDict()
            for cell in cells:
                if len(cells) == 21:
                    rosters_data[pk]['fields']['rank'] = int(cells[2].string)
                    s = stats_fields(s,3,cells)
                else:
                    rosters_data[pk]['fields']['rank'] = int(cells[1].string)
                    s = stats_fields(s,2,cells)
            stats_data.append(s)
    return make_free_agents(stats_data)

def make_free_agents(stats_data):
    sheet = 'https://docs.google.com/spreadsheets/d/1rJEY7dQSCD2523roGN_bFxeAowejpoKlTK-mOrCNeLs/edit#gid=1467451328'
    page = urlopen(sheet)
    soup = BeautifulSoup(page,'lxml')
    rows = soup.find_all('tr')
    free_agents_data = []
    pk = (len(players)+1)
    for row in rows[3:]:
        cells = row.find_all('td')
        name = cells[0].string
        if name in players:
            break
        f = OrderedDict()
        f['pk'] = pk
        f['model'] = 'usc_app.FreeAgent'
        f['fields'] = OrderedDict()
        if len(cells) >= 9:
            # name = cells[0].string
            if name == None:
                name = cells[0].get_text()
            free_agents_data.append(make_user(name,pk))
            f['fields']['user'] = pk
            f['fields']['name'] = name
            f['fields']['eligible'] = True
            s = cells[2].string.split('/')
            server = s[0]
            if server in SERVER_CHOICES:
                f['fields']['server'] = (SERVER_CHOICES.index(server))+1
            else:
                f['fields']['server'] = 9

            position = cells[3].string
            f['fields']['position'] = (POSITION_CHOICES.index(position))+1 if position in POSITION_CHOICES else 5

            mic = cells[4].string
            f['fields']['mic'] = True if mic == 'Yes' else False

            tagpro_profile = cells[5].string
            f['fields']['tagpro_profile'] = tagpro_profile

            reddit_info = cells[6].string
            f['fields']['reddit_info'] = reddit_info

            tagpro_stats = cells[7].string
            f['fields']['tagpro_stats'] = tagpro_stats

            if len(cells) == 9:
                previous_row = rows[(rows.index(row)-1)]
                previous_cells = previous_row.find_all('td')
                f['fields']['additional_notes'] = previous_cells[9].string
            else:
                f['fields']['additional_notes'] = cells[9].string
            free_agents_data.append(f)
            pk += 1
    free_agents_data += stats_data
    return free_agents_data

def make_user(player,pk):
    u = OrderedDict()
    u['pk'] = pk
    u['model'] = 'usc_app.User'
    u['fields'] = OrderedDict()
    u['fields']['username'] = player
    u['fields']['password'] = 'pbkdf2_sha256$24000$hYndqK3AJv8T$NtDFdGkRdF606dhY8FkbJFzw0lzqCgBA129CMktLHsk='
    return u

def stats_fields(dic,pointer,cells):
    s = dic
    i = pointer
    if cells[i].string is None: #3/2
        s['fields']['change'] = 0
    else:
        if cells[i].string[0] == '▼':
            s['fields']['change'] = -(int(cells[i].string[1:]))
        else:
            if cells[i].string[1] == '▼':
                s['fields']['change'] = int(cells[i].string[2:])
            else:
                s['fields']['change'] = int(cells[i].string[1:])
    i+=1
    s['fields']['team'] = cells[i].string #4/3
    s['fields']['abv'] = 'temp'
    i+=2
    if cells[i].string is None: #6/5
        s['fields']['streak'] = 0
    elif cells[i].string[-1] == 'L':
        s['fields']['streak'] = -(int(cells[i].string[:-1]))
    elif cells[i].string[-1] == 'W':
        s['fields']['streak'] = int(cells[i].string[:-1])
    else:
        s['fields']['streak'] = 0
    i+=1

    s['fields']['highestRank'] = int(cells[i].string) if cells[i].string is not None else 0  #7/6
    i+=1
    try: #/8/7
        int(cells[i].string)
        s['fields']['uscmRank'] = int(cells[i].string)
    except ValueError:
        s['fields']['uscmRank'] = 0
    i+=1
    date = cells[i].string.split('/') #9/8
    fixed_date = date[2]+'-'+date[0]+'-'+date[1]
    s['fields']['lastActive'] = fixed_date
    i+=1
    # s['fields']['challengeOut'] = int(cells[i].string)
    i+=1
    # s['fields']['challengeIn'] = int(cells[i].string)
    i+=1
    s['fields']['GP'] = int(cells[i].string)
    i+=1
    s['fields']['W'] = int(cells[i].string)
    i+=1
    s['fields']['L'] = int(cells[i].string)
    i+=1
    s['fields']['D'] = int(cells[i].string)
    i+=1
    s['fields']['F'] = int(cells[i].string)
    i+=1
    s['fields']['CF'] = int(cells[i].string)
    i+=1
    s['fields']['CA'] = int(cells[i].string)
    i+=1
    s['fields']['CD'] = int(cells[i].string)
    i+=1
    if cells[i].string == '-':
        s['fields']['CDperG'] = 0
    else:
        s['fields']['CDperG'] = float(cells[i].string)
    return s



def assign_player(finished):
    if 'captain' not in finished['fields']:
        return 'captain'
    elif 'co_captain' not in finished['fields']:
        return 'co_captain'
    elif 'member1' not in finished['fields']:
        return 'member1'
    elif 'member2' not in finished['fields']:
        return 'member2'
    elif 'member3' not in finished['fields']:
        return 'member3'
    elif 'member4' not in finished['fields']:
        return 'member4'
    elif 'member5' not in finished['fields']:
        return 'member5'
    elif 'member6' not in finished['fields']:
        return 'member6'

make_data()
