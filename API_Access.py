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



class ApiAccess:
    def __init__(self, db , seed):
        self.seed = seed
        self.db = db
        self.HEADERS = {"X-Riot-Token": API_Key}

    def get_player_matches(self, max_recency=7):
        match_list =self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + self.seed + "/ids?type=ranked&start=0&count=100")
        for match_id in match_list:
            if not self.db.check_match_in_queue(match_id):
                self.db.insert_match_queue(match_id)
                match_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id)
                save_match(match_id, match_data, (match_dir + match_data["info"]["gameVersion"]))
                print("saved match " + match_id)
                time.sleep(2)


    @staticmethod
    def get_match_participants(match_list : list):
        for match_id in match_list:
            match_data = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id, headers=self.HEADERS).json()
            game_version = match_data["info"]
            match_date = datetime.fromtimestamp(match_data["info"]["gameCreation"] / 1000)
            match_age = datetime.now() - match_date
            print(match_age < timedelta(days=7))

            print(datetime.now() - match_date)
            time.sleep(1.5)
            break

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

