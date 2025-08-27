from datetime import datetime, timezone
import psycopg2
import json
import os

class DBConnection:

    def __init__(self):
        self.conn = psycopg2.connect(database = "riot_data",
                        user = "postgres",
                        host = "localhost",
                        password = "UniProj26",
                        port = "5432")
        self.cur = self.conn.cursor()

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def insert_match_queue(self,match_id, date):
        self.cur.execute(f"INSERT INTO match_queue (match_id, date_scraped, scraped) VALUES ('{match_id}','{date}','True')")
        self.conn.commit()

    def check_match_in_queue(self,match_id):
        self.cur.execute(f"SELECT * FROM match_queue WHERE match_id='{match_id}';")
        if self.cur.fetchall():
            return True
        return False

    def match_scraped(self, match_id):
        self.cur.execute(f"SELECT * FROM match_queue WHERE match_id = '{match_id}' AND scraped = 'True'")
        if self.cur.fetchall():
            return True
        return False

    def insert_player(self, puuid, region, last_scraped, rank, division, lp):
        self.cur.execute(f"INSERT INTO players (puuid, region, last_scraped, current_rank, current_division, current_lp) VALUES ('{puuid}','{region}','{last_scraped}','{rank}','{division}','{lp}') "
                         f"ON CONFLICT (puuid) DO UPDATE SET last_scraped = '{last_scraped}', current_rank = '{rank}', current_division ='{division}', current_lp = '{lp}'")
        print("inserted player to DB")
        self.conn.commit()

