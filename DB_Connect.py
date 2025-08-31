import psycopg2
from psycopg2.extras import DictCursor
from creds import DBPASS

class DBConnection:

    def __init__(self):
        self.conn = psycopg2.connect(database = "riot_data",
                        user = "postgres",
                        host = "localhost",
                        password = DBPASS,
                        port = "5432")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    #inserts player (not match participant) into database to be scraped
    def insert_player(self, puuid, region):
        self.cur.execute(f"INSERT INTO players (puuid, region) VALUES ('{puuid}','{region}') ON CONFLICT DO NOTHING")
        #Checks rows affected by execute, if > 0 means player was inserted else record already exists
        if self.cur.rowcount > 0:
            print("Inserted player")
        else:
            print("Player already exists")
        self.conn.commit()

    def insert_rank(self, puuid, rank, division, lp, snapshot_date):
        self.cur.execute(f"INSERT INTO rank_snapshots (puuid, rank, division, lp, snapshot_date) "
                         f"VALUES ('{puuid}','{rank}','{division}','{lp}','{snapshot_date}')")
        self.conn.commit()

    #checks if player's rank has already been scraped
    def check_player_rank(self, puuid):
        #RETURN RANK, DATETIME OF SCRAPE
        self.cur.execute(f"SELECT * FROM rank_snapshots WHERE puuid = '{puuid}'")
        player = self.cur.fetchone()
        if player:
            return player
        return False

    def insert_match_id(self, match_id):
        self.cur.execute(f"INSERT INTO MATCHES (match_id) VALUES ('{match_id}')")
        self.conn.commit()

    #inserts match into database
    def insert_match(self, match_id, game_start, game_duration, patch_version, raw_data, rank_tier):
        self.cur.execute(f"UPDATE matches "
                         f"SET game_start = '{game_start}', game_duration = '{game_duration}', patch_version = '{patch_version}', raw_data = '{raw_data}', rank_tier = '{rank_tier}' "
                         f"WHERE match_id = '{match_id}'")
        self.conn.commit()

    #checks if match is already saved in database
    def match_saved(self, match_id : str) -> bool:
        self.cur.execute(f"SELECT 1 FROM matches WHERE match_id = '{match_id}'")
        if self.cur.fetchone():
            print("match exists")
            return True
        return False

    #sets scraped to true if player's match history is accessed
    def set_player_scraped(self, puuid, date):
        self.cur.execute(f"UPDATE players SET scraped = 'True' , last_scraped = '{date}' WHERE puuid = '{puuid}'")
        self.conn.commit()

    #sets scrape_complete to true if all valid games have been scraped from the player
    def set_scrape_complete(self, puuid):
        self.cur.execute(f"UPDATE players SET scrape_complete = 'True' WHERE puuid = '{puuid}'")
        self.conn.commit()

    def insert_participant(self,match_id, participant_data):
        self.cur.execute(f"INSERT INTO participants (match_id, puuid, win, champion_id, champion_name, team_id, lane, kills, deaths, assists, gold_earned, gold_spent, cs, damage_dealt, vision_score, champion_level) "
                         f"VALUES ('{match_id}','{participant_data["puuid"]}','{participant_data["win"]}','{participant_data["championId"]}','{participant_data["championName"]}',"
                         f"'{participant_data["teamId"]}','{participant_data["teamPosition"]}','{participant_data["kills"]}','{participant_data["deaths"]}','{participant_data["assists"]}',"
                         f"'{participant_data["goldEarned"]}','{participant_data["goldSpent"]}','{(participant_data["totalMinionsKilled"] + participant_data["neutralMinionsKilled"])}',"
                         f"'{participant_data["totalDamageDealtToChampions"]}','{participant_data["visionScore"]}','{participant_data["champLevel"]}')")
        self.conn.commit()