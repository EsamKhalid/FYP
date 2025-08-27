import json

from DB_Connect import DB_Connection
from File_Save import save_match
import DB_Connect

from creds import API_Key
import requests
from datetime import datetime, timezone, timedelta
import time
import os

match_dir = r"C:/Api_Data/match_data/EUW/"

current_patch = 15.17
prev_patch = 15.16
acceptable_patch = 15.15

rank_map = {
    "Iron IV": 0, "Iron III": 1, "Iron II": 2, "Iron I": 3,
    "Bronze IV": 4, "Bronze III": 5, "Bronze II": 6, "Bronze I": 7,
    "Silver IV": 8, "Silver III": 9, "Silver II": 10, "Silver I": 11,
    "Gold IV": 12, "Gold III": 13, "Gold II": 14, "Gold I": 15,
    "Platinum IV": 16, "Platinum III": 17, "Platinum II": 18, "Platinum I": 19,
    "Emerald IV": 20, "Emerald III": 21, "Emerald II": 22, "Emerald I": 23,
    "Diamond IV": 24, "Diamond III": 25, "Diamond II": 26, "Diamond I": 27,
    "Master": 28, "Grandmaster": 29, "Challenger": 30
}

int_to_rank = {v: k for k, v in rank_map.items()}

class ApiAccess:
    def __init__(self, db , seed):
        self.seed = seed
        self.db = db
        self.HEADERS = {"X-Riot-Token": API_Key}

    def get_player_matches(self, max_recency=7):
        match_list =self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + self.seed + "/ids?type=ranked&start=0&count=100")
        for match_id in match_list:
            if not self.db.match_scraped(match_id):
                self.db.insert_match_queue(match_id)
                match_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id)
                #save_match(match_id, match_data, (match_dir + match_data["info"]["gameVersion"]))
                print("saved match " + match_id)
                time.sleep(2)


    #IF THE PATCH IS TOO OLD, REMOVE ALL MATCHES FROM QUEUE FROM THE PUUID

    def get_average_rank(self, rankList : list[str]) -> int:
        total = 0
        for rank in rankList:
            total += rank_map[rank]
        total = round(total / 10)
        return total

    def get_match_participants(self,match_data):
        rank_list = []
        for participant in match_data["metadata"]["participants"]:
            self.api_call(f"https://europe.api.riotgames.com/lol/league/v4/entries/by-puuid/{participant}")

    # def get_match_participants(self, match_list : list):
    #     for match_id in match_list:
    #         match_data = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id, headers=self.HEADERS).json()
    #         game_version = match_data["info"]
    #         match_date = datetime.fromtimestamp(match_data["info"]["gameCreation"] / 1000)
    #         match_age = datetime.now() - match_date
    #         print(match_age < timedelta(days=7))
    #
    #         print(datetime.now() - match_date)
    #         time.sleep(1.5)
    #         break

    def api_call(self, url :str, max_retries = 3) -> json:
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.HEADERS, timeout=10)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After'), 60)
                    print(f"Rate limited, waiting {retry_after} seconds")
                    time.sleep(retry_after + 120)
                elif response.status_code == 404:
                    return None
                else:
                    print(f"API error {response.status_code}")
                    time.sleep(2 ** attempt)

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(2 ** attempt)
        return None

    # def store_match(patch_version):
    #     filePath = match_dir + "1.2.3"
    #     if os.path.exists(filePath):
    #         print("exists")
    #     else:
    #         os.mkdir(filePath)
    #         print("created")
    #

