import json
from typing import Any

from DB_Connect import DBConnection
from File_Save import save_match, save_timeline

from creds import API_KEY
import requests
from datetime import datetime, timezone, timedelta
import time
import os #temp

# Directories where raw files are stored
match_dir = r"C:/Api_Data/match_data/EUW/"
timeline_dir = r"C:/Api_data/timeline_data/EUW/"

player_match_dir = r"C:/Api_Data/player_matches/match_data/EUW/"
player_timeline_dir = r"C:/Api_Data/player_matches/timeline_data/EUW/"

# Assigns a number to each rank for average rank calculation
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

# Desired distribution of match ranks
desired_distribution = {"IRON" : 0.1, "BRONZE" : 0.1,
                      "SILVER" : 0.15, "GOLD" : 0.15,
                      "PLATINUM" : 0.1, "EMERALD" : 0.1, "DIAMOND" : 0.1,
                      "MASTER" : 0.066, "GRANDMASTER" : 0.067, "CHALLENGER" : 0.067}

class ApiAccess:
    def __init__(self, db : DBConnection):
        # DBConnection class instance
        self.db = db

        # Headers used for api calls
        self.HEADERS = {"X-Riot-Token": API_KEY}

    # Main loop for scraping a player
    def get_player_matches(self,seed : str, seed_rank : str, seed_division : str):
        print("scraping " + seed)

        # Gets list of matches played by seed player
        match_list = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + seed + "/ids?queue=420&type=ranked&start=0&count=35")
        self.db.set_player_scraped(seed, datetime.now(timezone.utc))

        # Loop through matches
        for match_id in match_list:
            if not self.db.match_saved(match_id):
                if not self.process_player_match(match_id, seed_rank, seed_division, seed):
                    break
        self.db.set_scrape_complete(seed)

        # Calculate next rank and fetch seed
        rank_needed = self.calculate_needed_rank()
        next_seed = self.db.get_seed(rank_needed)["puuid"]
        rank = self.db.get_player_rank(next_seed)
        seed_rank = rank["current_rank"]
        seed_division = rank["current_division"]

        # Calls itself using next seed
        self.get_player_matches(next_seed,seed_rank, seed_division)

    # Process match to add to database
    def process_match(self, match_id : str):
        print("Processing Match " + match_id)
        start = time.time()
        self.db.insert_match_id(match_id)

        # Fetch match data from API
        match_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id)

        # Stops if game is not ranked
        if match_data["info"]["queueId"] != 420:
            print("not ranked")
            return True

        # Calculates game age and breaks loop if match scraped is > 7 days old (for rank accuracy)
        print("match date " + str(datetime.fromtimestamp(match_data["info"]["gameStartTimestamp"] / 1000)))
        game_start = datetime.fromtimestamp(match_data["info"]["gameStartTimestamp"] / 1000)
        if (datetime.now() - game_start) > timedelta(days=7):
            self.db.remove_match_id(match_id)
            print("Scraped last 7 days")
            return False
        game_duration = match_data["info"]["gameDuration"]

        # Stops if game is under 15 minutes
        if game_duration < 900:
            self.db.remove_match_id(match_id)
            return False

        # Calculates average rank of match
        average_rank = int_to_rank[self.get_match_participants(match_data)].split(" ")

        # Saves match to disk and inserts to database
        save_match(match_id, match_data, (match_dir + match_data["info"]["gameVersion"]))
        self.db.insert_match(match_id, game_start, match_data["info"]["gameDuration"],match_data["info"]["gameVersion"], average_rank[0], average_rank[1])
        timeline_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id + "/timeline")
        save_timeline(match_id, timeline_data, timeline_dir, match_data["info"]["gameVersion"])
        print("saved match " + match_id)
        print("Finished in " + str(round(time.time() - start)) + " seconds")
        return True


    def process_player_match(self, match_id :str, seed_rank : str, seed_division : str, seed_puuid : str):
        print("Processing Match: " + match_id)
        match_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id)
        if match_data["info"]["queueId"] != 420:
            print("not ranked")
            return False
        game_duration = match_data["info"]["gameDuration"]
        if game_duration < 900:
            return False

        patch_version = match_data["info"]["gameVersion"]

        save_match(match_id, match_data, (player_match_dir + match_data["info"]["gameVersion"]))
        timeline_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id + "/timeline")
        save_timeline(match_id, timeline_data, player_timeline_dir, match_data["info"]["gameVersion"])

        self.db.insert_player_match(match_id, patch_version, seed_rank, seed_puuid, seed_division)
        return True

    # Calculates average rank of match using dict
    @staticmethod
    def get_average_rank(rank_list : list[str]) -> int:
        total = 0
        for rank in rank_list:
            total += rank_map[rank]
        total = round(total / 10)
        return total

    # Processes match participants from each match
    def get_match_participants(self,match_data : json) -> int:
        rank_list = []
        for participant in match_data["info"]["participants"]:
            player = participant["puuid"]

            # Inserts player and participant into database
            self.db.insert_player(player, "EUW")
            self.db.insert_participant(match_data["metadata"]["matchId"],participant)
            # checks player presence in database
            db_player = self.db.check_player_rank(player)
            if db_player:
                time_diff = datetime.now(timezone.utc) - db_player["rank_date"]
                # If rank hasn't been accessed recently, rescrape rank and update in db
                if time_diff > timedelta(days=7) or time_diff < timedelta(days=-7):
                    ranks = self.get_player_rank(player)
                else:
                    ranks = {"rank" : db_player["current_rank"], "division" : db_player["current_division"], "lp" : db_player["current_lp"]}
            else:
                ranks = self.get_player_rank(player)
            if not ranks:
                continue
            rank_list.append(ranks["rank"] + " " + ranks["division"])

        # Returns average rank of participants
        return self.get_average_rank(rank_list)

    # Gets rank of player
    def get_player_rank(self, puuid : str) -> dict[str, Any]:

        # Queries API for rank
        response = self.api_call(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}")

        # Removes non ranked player from database
        if not response:
            self.db.remove_player(puuid)
            return None

        # If ranked in multiple modes, selects only ranked solo
        if len(response) > 1:
            if response[0]["queueType"] == "RANKED_SOLO_5x5":
                player_details = response[0]
            else:
                player_details = response[1]
        else:
            player_details = response[0]

        # Updates player table with rank
        rank = player_details["tier"]
        division = player_details["rank"]
        lp = player_details["leaguePoints"]
        self.db.update_rank(puuid, rank, division, lp, datetime.now(timezone.utc))
        return {"rank" : rank, "division" : division, "lp" : lp}

    # Calculates rank furthest from desired distribution
    def calculate_needed_rank(self) -> str:
        ranks = self.db.get_matches_ranks()
        match_count = self.db.get_matches_count()[0]["count"]
        rank_distribution = {}
        distribution_ratios = {}
        for rank in ranks:
            if not rank["seed_rank"]:
                self.complete_incomplete_matches()
                continue

            # Actual percentage of rank in database
            rank_distribution[rank["seed_rank"]] = (rank["match_count"] / match_count)

            # Ratio needed to reach desired distribution
            distribution_ratios[rank["seed_rank"]] = round(desired_distribution[rank["seed_rank"]] / rank_distribution[rank["seed_rank"]],2)
        print(distribution_ratios)
        reverse_dist_ratios = {v: k for k, v in distribution_ratios.items()}
        print("Needed Rank: " + reverse_dist_ratios[max(distribution_ratios.values())])

        # Returns needed rank
        return reverse_dist_ratios[max(distribution_ratios.values())]

    # Similar to calculate needed rank but only displays composition
    def get_rank_composition(self):
        ranks = self.db.get_matches_ranks()
        match_count = self.db.get_matches_count()[0]["count"]
        rank_distribution = {}
        distribution_ratios = {}
        for rank in ranks:
            if not rank["rank"]:
                self.complete_incomplete_matches()
                continue
            rank_distribution[rank["rank"]] = round((rank["match_count"] / match_count),2)
            distribution_ratios[rank["rank"]] = round(desired_distribution[rank["rank"]] / rank_distribution[rank["rank"]], 2)
        print(rank_distribution)
        print(distribution_ratios)

    # Re-scrapes any incomplete matches
    def complete_incomplete_matches(self):
        match_list = self.db.get_incomplete_matches()
        for match in match_list:
            self.process_match(match["match_id"])

    # Method to handle api calls
    def api_call(self, url : str, max_retries = 3) -> json:
        for attempt in range(max_retries):
            try:
                # API call using requests library
                response = requests.get(url, headers=self.HEADERS, timeout=10)

                # Success
                if response.status_code == 200:
                    time.sleep(1.6)
                    return response.json()

                # Rate limit hit
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After'), 60)
                    print(f"Rate limited, waiting {retry_after} seconds")
                    time.sleep(retry_after + 120)

                # Not found
                elif response.status_code == 404:
                    return None
                else:
                    print(f"API error {response.status_code}")
                    time.sleep(2 ** attempt)

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(2 ** attempt)
        return None

    # Methods below were made for specific situations that arose during the development process --------------------------------------------------------

    # Made specifically for rank_snapshot merge to players
    def update_player_ranks(self):
        players = self.db.query_players()
        for player in players:
            player_rank = self.db.query_rank(player["puuid"])
            if not player_rank:
                continue
            self.db.update_rank(player["puuid"],player_rank["rank"], player_rank["division"], player_rank["lp"], player_rank["snapshot_date"])

    # Made specifically for rank-division split in matches
    def update_match_ranks(self):
        matches = self.db.query_matches()
        for match in matches:
            rank_split = match["rank"].split(" ")
            self.db.update_rank_division(match["match_id"], rank_split[0], rank_split[1])

    # Made to re scrape the players after forgetting to filter out ranked flex
    def rescrape_players(self):
        players = self.db.query_players()
        player_count = len(players)
        count = 1
        for player in players:
            print(f"Player {count} / " + str(player_count))
            self.get_player_rank(player["puuid"])
            count += 1

    # Made to re rank the matches after player ranks were rescraped
    def rerank_matches(self):
        matches = self.db.query_matches()
        for match in matches:
            #print(match["raw_data"]["info"]["queueId"])
            # if match["raw_data"]["info"]["queueId"] == 420:
            #     print("ok")
            # else:
            #     self.db.remove_participants(match["match_id"])
            #     self.db.remove_match_id(match["match_id"])
            #     print("removed match")
            average_rank = int_to_rank[self.get_match_participants(match["raw_data"])].split(" ")
            rank = [match["rank"] , match["division"]]
            if average_rank != rank:
                print("updated rank")
                print(average_rank, rank)
            self.db.update_rank_division(match["match_id"], average_rank[0], average_rank[1])

    def insert_match_data(self):
        matches = self.db.query_matches()
        for match in matches:
            self.db.insert_match_data(match["match_id"], match["raw_data"])
            print("inserted into " + match["match_id"])
            pass

    tempdir = r"C:/Api_Data/match_data/EUW/15.16.706.7476"

    def insert_old_matches(self):
        for file in os.listdir(r"C:/Api_Data/match_data/EUW/15.18.710.2811"):
            filename = os.fsdecode(file).split("_")
            self.db.ins_mat(filename[0] + "_" +  filename[1])
            print(filename[0] + "_" +  filename[1])

    def ins(self):
        matches = self.db.get_mat()
        for match in matches:
            match_id = match["match_id"]
            if not self.db.match_saved(match_id):
                if not self.db.check_match(match_id):
                    continue
                if not self.process_match(match_id):
                    continue

    def insert_timeline(self, match_id : str, patch : str):
        if not self.db.timeline_saved(match_id):
            timeline_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id + "/timeline")
            save_timeline(match_id, timeline_data, timeline_dir, patch)
            self.db.insert_timeline_data(match_id, json.dumps(timeline_data))

    def populate_timeline(self):
        matches = self.db.query_matches()
        for match in matches:
            match_id = match["match_id"]
            patch = match["patch_version"]
            print("inserting " + match_id)
            self.insert_timeline(match_id, patch)

    def save_timelines(self):
        matches = self.db.query_matches()
        for match in matches:
            match_id = match["match_id"]
            patch = match["patch_version"]
            if not self.db.timeline_saved(match_id):
                timeline_data = self.api_call("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id + "/timeline")
                save_timeline(match_id, timeline_data, timeline_dir, patch)
                self.db.insert_timeline(match_id)
                print("timeline_saved")



