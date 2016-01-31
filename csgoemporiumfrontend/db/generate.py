from datetime import datetime
from dateutil.relativedelta import relativedelta
from psycopg2.extras import Json
import json, random, os

cur_dir = os.path.dirname(__file__)


ONE_WEEK_FUTURE = datetime.utcnow() + relativedelta(weeks=1)

USERS = [
    ("76561198037632722", "super"),
    ("76561198031651584", "normal"),
]

def generate_users(t):
    for user in USERS:
        t.execute("INSERT INTO users (steamid, active, ugroup) VALUES (%s, %s, %s)",
            (user[0], True, user[1]))

GAME = {
    "name": "CS:GO",
    "appid": 730,
    "active": True,
}

def generate_games(t):
    t.execute("INSERT INTO games (name, appid, active) VALUES (%(name)s, %(appid)s, %(active)s)",
        GAME)

TEAMS = [
    ("c9", "Cloud9", "/static/img/teams/cloud9.png"),
    ("fnatic", "Fnatic", "/static/img/teams/fnatic.png"),
    ("HellRaisers", "HellRaisers", "/static/img/teams/hellraisers.png"),
    ("dignitas", "Team Dignitas", "/static/img/teams/dignitas.png"),
    ("nip", "Ninjas In Pajamas", "/static/img/teams/nip.png"),
    ("virtus.pro", "Virtus Pro", "/static/img/teams/virtuspro.png"),
    ("CLG", "Counter Logic Gaming", "http://clgaming.net/interface/img/ogImage.jpg")
]

def generate_teams(t):
    for team in TEAMS:
        t.execute("INSERT INTO teams (tag, name, logo) VALUES (%s, %s, %s)", team)

MATCHES = [
    {
        "game": 1,
        "teams": [1, 5],
        "meta": {
            "league": {
                "name": "CEVO",
                "info": None,
                "splash": "http://i.imgur.com/x9zkVjg.png",
                "logo": "http://i.imgur.com/8VIcWM2.png"
            },
            "type": "BO1",
            "streams": ["http://twitch.tv/test1", "http://twitch.tv/test2"],
            "maps": ["de_nuke"]
        },
        "lock_date": ONE_WEEK_FUTURE,
        "match_date": ONE_WEEK_FUTURE,
        "public_date": datetime.utcnow()
    },
    {
        "game": 1,
        "teams": [3, 4],
        "meta": {
            "league": {
                "name": "ESEA",
                "info": None,
                "splash": "http://i.imgur.com/cQ88n4A.png",
                "logo": "http://i.imgur.com/KCZZVDH.jpg"
            },
            "note": "This is a test note!",
            "type": "BO3",
            "streams": ["http://mlg.tv/swag", "http://twitch.tv/esea"],
            "maps": ["de_nuke", "de_mirage", "de_dust2"]
        },
        "lock_date": ONE_WEEK_FUTURE,
        "match_date": ONE_WEEK_FUTURE,
        "public_date": datetime.utcnow()
    }
]

MATCH_QUERY = """
INSERT INTO matches (game, teams, meta, lock_date, match_date, public_date, active) VALUES
(%(game)s, %(teams)s, %(meta)s, %(lock_date)s, %(match_date)s, %(public_date)s, true);
"""

def generate_matches(t):
    for match in MATCHES:
        match['meta'] = Json(match['meta'])
        t.execute(MATCH_QUERY, match)

BETS = [
    {
        "better": 2,
        "match": 1,
        "team": random.choice([0, 1]),
        "value": random.randint(1, 60),
        "items": [(random.randint(1, 25), 'NULL', 'NULL') for i in range(4)],
        "state": "confirmed",
        "created_at": datetime.utcnow(),
    } for i in range(300)
]

BET_QUERY = """
INSERT INTO bets (better, match, team, value, items, state, created_at) VALUES
(%(better)s, %(match)s, %(team)s, %(value)s, ARRAY[{}], %(state)s, %(created_at)s);
"""

# TODO
def generate_bets(t):
    for entry in BETS:
        data = entry['items']
        del entry['items']
        q = BET_QUERY.format(', '.join(map(lambda i: ("(%s, %s, %s, '{}')" % i) + "::steam_item", data)))
        t.execute(q, entry)

DATA_GENERATORS = [
    generate_users,
    generate_games,
    generate_teams,
    generate_matches,
    generate_bets
]

