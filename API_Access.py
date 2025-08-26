import json

from creds import API_Key
import requests
from datetime import datetime, timezone, timedelta
import time
import os

match_dir = r"C:/Api_Data/match_data/EUW/"

HEADERS = {"X-Riot-Token": API_Key}

#seed account = rank 1 player euw
seed_account ="aSstdTtqhoNflYWFsjsvT1Zg_u0-mJltk_qJ3v80YXazwUlsakbuNzZ8Dsb62jARsH2fbn6rM2q6Ug"

#challenger_list = requests.get("https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5", headers=headers).json()


def get_player_matches(puuid, max_recency = 7):
    match_list = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+seed_account+"/ids?type=ranked&start=0&count=100", headers=HEADERS).json()
    return match_list


def get_match_participants(matchList):
    for match_id in matchList:
        match_data = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id,headers=HEADERS).json()
        match_date = datetime.fromtimestamp(match_data["info"]["gameCreation"] / 1000)
        match_age = datetime.now() - match_date
        print(match_age > timedelta(days=7))

        print(datetime.now() - match_date)
        time.sleep(1.5)


def store_match(patch_version):
    filePath = match_dir + "1.2.3"
    if os.path.exists(filePath):
        print("exists")
    else:
        os.mkdir(filePath)
        print("created")

#store_match()

get_match_participants(get_player_matches(seed_account))