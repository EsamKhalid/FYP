import json
from typing import Any

from DB_Connect import DBConnection
from File_Save import save_match

from creds import API_Key
import requests
from datetime import datetime, timezone, timedelta
import time

import sys #for debugging

current_patch = 15.17
prev_patch = 15.16
acceptable_patch = 15.15

rank_map = {
    "IRON IV": 0, "IRON III": 1, "IRON II": 2, "IRON I": 3,
    "BRONZE IV": 4, "BRONZE III": 5, "BRONZE II": 6, "BRONZE I": 7,
    "SILVER IV": 8, "SILVER III": 9, "SILVER II": 10, "SILVER I": 11,
    "GOLD IV": 12, "GOLD III": 13, "GOLD II": 14, "GOLD I": 15,
    "PLATINUM IV": 16, "PLATINUM III": 17, "PLATINUM II": 18, "PLATINUM I": 19,
    "EMERALD IV": 20, "EMERALD III": 21, "EMERALD II": 22, "EMERALD I": 23,
    "DIAMOND IV": 24, "DIAMOND III": 25, "DIAMOND II": 26, "DIAMOND I": 27,
    "MASTER I": 28, "GRANDMASTER I": 29, "CHALLENGER I": 30
}

int_to_rank = {v: k for k, v in rank_map.items()}

class ApiAccess:
    def __init__(self, db : DBConnection , seed):
        self.seed = seed
        self.db = db
        self.HEADERS = {"X-Riot-Token": API_Key}

    def get_player_matches(self,seed : str ,max_recency=7):
        #SEED SHOULD BE THE FIRST NON SCRAPED PLAYER IN PLAYER LIST
        match_list = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + self.seed + "/ids?type=ranked&start=0&count=100")
        for match_id in match_list:
            if not self.db.match_saved(match_id):
                match_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id)
                #caclulate average rank for all players
                average_rank = int_to_rank[self.get_match_participants(match_data,seed)]
                game_start = datetime.fromtimestamp(match_data["info"]["gameStartTimestamp"] / 1000)
                #saves match to disk
                save_match(match_id, match_data, (match_dir + match_data["info"]["gameVersion"]))
                #inserts match to database
                self.db.insert_match(match_id, game_start, match_data["info"]["gameDuration"], match_data["info"]["gameVersion"], json.dumps(match_data), average_rank)
                print("saved match " + match_id)
                break
                time.sleep(1.2)
        self.db.set_scrape_complete(seed)

    @staticmethod
    def get_average_rank(rank_list : list[str]) -> int:
        total = 0
        for rank in rank_list:
            total += rank_map[rank]
        total = round(total / 10)
        return total

    def get_match_participants(self,match_data : json, seed : str) -> int:
        rank_list = []
        for participant in match_data["info"]["participants"]:
            player = participant["puuid"]

            self.db.insert_participant(participant)

            sys.exit("debug")
            #attempts to access player in database
            db_player = self.db.check_player_rank(player)
            if db_player:
                db_player = db_player[0]
                time_diff = datetime.now(timezone.utc) - db_player["last_rank_check"]
                #if player rank has not been scraped recently, rescrape for rank accuracy
                if time_diff > timedelta(days=7) or time_diff < timedelta(days=-7):
                    ranks = self.get_player_rank(player)
                    time.sleep(1.2)
                else:
                    ranks = {"rank" : db_player["current_rank"], "division" : db_player["current_division"], "lp" : db_player["current_lp"]}
                    print("Player already exists in DB")
            else:
                #if player does not exist in database at all
                ranks = self.get_player_rank(player)
                #if player is the seed player, set scraped to true
                if player == seed:
                    self.db.set_player_scraped(player)
                time.sleep(1.2)

            rank_list.append(ranks["rank"] + " " + ranks["division"])
            print("Rank: " + ranks["rank"] + " " + ranks["division"])

        return self.get_average_rank(rank_list)

    def get_player_rank(self, puuid : str) -> dict[str, Any]:
        player_details = self.api_call(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}")[0]
        rank = player_details["tier"]
        division = player_details["rank"]
        lp = player_details["leaguePoints"]
        self.db.insert_player(puuid, "EUW", datetime.now(timezone.utc), rank, division, lp)
        return {"rank" : rank, "division" : division, "lp" : lp}

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
