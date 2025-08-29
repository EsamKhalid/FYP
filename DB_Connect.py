import psycopg2
from psycopg2.extras import DictCursor


class DBConnection:

    def __init__(self):
        self.conn = psycopg2.connect(database = "riot_data",
                        user = "postgres",
                        host = "localhost",
                        password = "UniProj26",
                        port = "5432")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def insert_player(self, puuid, region, last_rank_check, rank, division, lp):
        self.cur.execute(f"INSERT INTO players (puuid, region, last_rank_check, current_rank, current_division, current_lp) VALUES ('{puuid}','{region}','{last_rank_check}','{rank}','{division}','{lp}') "
                         f"ON CONFLICT (puuid) DO UPDATE SET last_rank_check = '{last_rank_check}', current_rank = '{rank}', current_division ='{division}', current_lp = '{lp}'")
        print("inserted player to DB")
        self.conn.commit()

    def check_player_rank(self, puuid):
        #RETURN RANK, DATETIME OF SCRAPE
        self.cur.execute(f"SELECT * FROM players WHERE puuid = '{puuid}'")
        player = self.cur.fetchall()
        if player:
            return player
        return False

    def insert_match(self, match_id, game_start, game_duration, patch_version, raw_data, rank_tier):
        self.cur.execute(f"INSERT INTO matches (match_id, game_start, game_duration, patch_version, raw_data, rank_tier) "
                         f"VALUES ('{match_id}','{game_start}','{game_duration}','{patch_version}','{raw_data}','{rank_tier}')")
        self.conn.commit()

    def match_saved(self, match_id : str) -> bool:
        self.cur.execute(f"SELECT 1 FROM matches WHERE match_id = '{match_id}'")
        if self.cur.fetchone():
            print("match exists")
            return True
        return False

    # def insert_match_queue(self,match_id, date):
    #     self.cur.execute(f"INSERT INTO match_queue (match_id, date_scraped, scraped) VALUES ('{match_id}','{date}','True')")
    #     self.conn.commit()
    #
    # def check_match_in_queue(self,match_id):
    #     self.cur.execute(f"SELECT * FROM match_queue WHERE match_id='{match_id}';")
    #     if self.cur.fetchall():
    #         return True
    #     return False
    #
    # def match_scraped(self, match_id):
    #     self.cur.execute(f"SELECT * FROM match_queue WHERE match_id = '{match_id}' AND scraped = 'True'")
    #     if self.cur.fetchall():
    #         return True
    #     return False
