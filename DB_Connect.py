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

    def get_seed(self, rank):
        self.cur.execute(f"SELECT puuid FROM players WHERE current_rank = '{rank}' AND scraped = 'false' ORDER BY rank_date ASC")
        return self.cur.fetchone()

    #inserts player (not match participant) into database to be scraped
    def insert_player(self, puuid, region):
        self.cur.execute(f"INSERT INTO players (puuid, region) VALUES ('{puuid}','{region}') ON CONFLICT DO NOTHING")
        #Checks rows affected by execute, if > 0 means player was inserted else record already exists
        if self.cur.rowcount > 0:
            print("Inserted player")
        else:
            print("Player already exists")
        self.conn.commit()

    #inserts rank to rank snapshot table
    def insert_rank(self, puuid, rank, division, lp, date):
        self.cur.execute(f"UPDATE players SET current_rank = '{rank}', current_division = '{division}', current_lp = '{lp}', rank_date = '{date}' where puuid = '{puuid}'")
        self.conn.commit()

    #checks if player's rank has already been scraped
    def check_player_rank(self, puuid):
        #RETURN RANK, DATETIME OF SCRAPE
        self.cur.execute(f"SELECT * FROM players WHERE puuid = '{puuid}'")
        player = self.cur.fetchone()
        rank = player["current_rank"]
        if rank:
            return player
        return False

    #inserts match id first to allow FK for participants table
    def insert_match_id(self, match_id):
        self.cur.execute(f"INSERT INTO MATCHES (match_id) VALUES ('{match_id}') ON CONFLICT DO NOTHING")
        self.conn.commit()

    #inserts match into database
    def insert_match(self, match_id, game_start, game_duration, patch_version, raw_data, rank, division):
        self.cur.execute(f"UPDATE matches "
                         f"SET game_start = '{game_start}', game_duration = '{game_duration}', patch_version = '{patch_version}', raw_data = '{raw_data}', rank = '{rank}', division = '{division}' "
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

    #inserts participant into participant table
    def insert_participant(self,match_id, participant_data):
        self.cur.execute(f"INSERT INTO participants (match_id, puuid, win, champion_id, champion_name, team_id, lane, kills, deaths, assists, gold_earned, gold_spent, cs, damage_dealt, vision_score, champion_level) "
                         f"VALUES ('{match_id}','{participant_data["puuid"]}','{participant_data["win"]}','{participant_data["championId"]}','{participant_data["championName"]}',"
                         f"'{participant_data["teamId"]}','{participant_data["teamPosition"]}','{participant_data["kills"]}','{participant_data["deaths"]}','{participant_data["assists"]}',"
                         f"'{participant_data["goldEarned"]}','{participant_data["goldSpent"]}','{(participant_data["totalMinionsKilled"] + participant_data["neutralMinionsKilled"])}',"
                         f"'{participant_data["totalDamageDealtToChampions"]}','{participant_data["visionScore"]}','{participant_data["champLevel"]}')")
        self.conn.commit()

    def remove_match_id(self, match_id):
        self.cur.execute(f"DELETE FROM matches WHERE match_id = '{match_id}'")
        self.conn.commit()

    def remove_participants(self,match_id):
        self.cur.execute(f"DELETE FROM participants WHERE match_id = '{match_id}'")
        self.conn.commit()

    def remove_player(self, puuid):
        self.cur.execute(f"DELETE FROM players WHERE puuid = '{puuid}'")
        self.conn.commit()

    def get_matches_ranks(self):
        self.cur.execute("SELECT rank, COUNT(*) AS match_count FROM matches GROUP BY rank ORDER BY match_count DESC")
        return self.cur.fetchall()

    def get_matches_count(self):
        self.cur.execute("SELECT COUNT(*) FROM matches")
        return self.cur.fetchall()

    def get_incomplete_matches(self):
        self.cur.execute(f"SELECT match_id FROM matches WHERE game_start IS NULL")
        return self.cur.fetchall()

    # Made specifically for rank-division split in matches
    def query_matches(self):
        self.cur.execute("SELECT * FROM matches")
        return self.cur.fetchall()

    # Made specifically for rank-division split in matches
    def update_rank_division(self, match_id, rank, division):
        self.cur.execute(f"UPDATE matches SET rank = '{rank}', division = '{division}' WHERE match_id = '{match_id}'")
        self.conn.commit()


    # Made specifically for rank_snapshot merge to players
    def query_players(self):
        self.cur.execute("SELECT * from players")
        return self.cur.fetchall()

    # Made specifically for rank_snapshot merge to players
    def update_rank(self, puuid, rank, division, lp, date):
        self.cur.execute(f"UPDATE players SET current_rank = '{rank}', current_division = '{division}', current_lp = '{lp}', rank_date = '{date}' where puuid = '{puuid}'")
        self.conn.commit()

    # Made specifically for rank_snapshot merge to players
    def query_rank(self,puuid):
        self.cur.execute(f"SELECT * FROM rank_snapshots WHERE puuid = '{puuid}'")
        print("updated rank")
        return self.cur.fetchone()

