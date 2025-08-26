from datetime import datetime, timezone
import psycopg2
import json
import os


match_folder = r"C:\Api_Data\match_data"

seed_account ="aSstdTtqhoNflYWFsjsvT1Zg_u0-mJltk_qJ3v80YXazwUlsakbuNzZ8Dsb62jARsH2fbn6rM2q6Ug"


class DB_Connection():

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


    def insert_match_queue(self,match_id):
        self.cur.execute(f"INSERT INTO match_queue (match_id) VALUES ({match_id})")
        self.conn.commit()

    def check_match_in_queue(self,match_id):
        self.cur.execute(f"SELECT * FROM match_queue WHERE match_id='{match_id}';")

        if self.cur.fetchall():
            return True

        return False


# conn = psycopg2.connect(database = "riot_data",
#                         user = "postgres",
#                         host = "localhost",
#                         password = "UniProj26",
#                         port = "5432")
#
# cur = conn.cursor()
#
#
#



#match_list = api.get_player_matches()

#print(api.get_match_participants(match_list))

#conn.commit()

#cur.close()
#conn.close()