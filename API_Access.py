import json

from creds import API_Key
import requests

player_list = r"C:/Api_Data/PlayerList.txt"
last_scraped_player = r"C:/Api_Data/Last_Scraped.txt"

headers = {"X-Riot-Token": API_Key}

#seed account = rank 1 player euw
seed_account ="aSstdTtqhoNflYWFsjsvT1Zg_u0-mJltk_qJ3v80YXazwUlsakbuNzZ8Dsb62jARsH2fbn6rM2q6Ug"

#challenger_list = requests.get("https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5", headers=headers).json()


def get_player_matches(puuid, max_recency = 7):
    match_list = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+seed_account+"/ids?type=ranked&start=0&count=20", headers=headers).json()
    return match_list


def get_match_participants(matchList):
    for match_id in matchList:
        match_data = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id,headers=headers).json()

        print(json.dumps(match_data, indent=4))
        break


get_match_participants(get_player_matches(seed_account))