import json
from difflib import get_close_matches

from DB_Connect import DB_Connection
from File_Save import save_match
import DB_Connect

from creds import API_Key
import requests
from datetime import datetime, timezone, timedelta
import time
import os

match_dir = r"C:/Api_Data/match_data/EUW/"

HEADERS = {"X-Riot-Token": API_Key}

db = DB_Connection()

print(db.check_match_in_queue("euw1"))
print(db.check_match_in_queue("euw2"))

class ApiAccess:

    def __init__(self, seed):
        self.seed = seed

    def get_player_matches(self, max_recency=7) -> list :
        match_list = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + self.seed + "/ids?type=ranked&start=0&count=100", headers=HEADERS).json()
        return match_list

    @staticmethod
    def get_match_participants(match_list : list):
        for match_id in match_list:
            match_data = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id, headers=HEADERS).json()
            #CREATE METHOD IN DB CONNECT TO CHECK IF MATCH ALREADY STORED

            if db.check_match_in_queue(match_id) == False:
                db.insert_match_queue(match_id)
                save_match(match_id, match_data, match_dir)

            game_version = match_data["info"]
            match_date = datetime.fromtimestamp(match_data["info"]["gameCreation"] / 1000)
            match_age = datetime.now() - match_date
            print(match_age < timedelta(days=7))

            print(datetime.now() - match_date)
            time.sleep(1.5)
            break

    def store_match(patch_version):
        filePath = match_dir + "1.2.3"
        if os.path.exists(filePath):
            print("exists")
        else:
            os.mkdir(filePath)
            print("created")


db.close_connection()

#store_match()


#get_match_participants(get_player_matches(seed_account))