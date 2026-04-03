import json
import pandas as pd
import os
import psycopg2
from psycopg2.extras import DictCursor, execute_values

from PythonScripts.creds import DBPASS


rootdir = "C:/Api_Data/combined/timeline_data/EUW"

rawParticipants = pd.read_csv("../data/participants.csv")

participants = pd.DataFrame(rawParticipants.set_index(["puuid", "match_id"])[["lane", "champion_name", "kills", "deaths", "assists", "vision_score"]].to_dict())

count = 0

class TimelineProcessor:

    def __init__(self):
        self.conn = psycopg2.connect(database="features_db",
                                     user="postgres",
                                     host="localhost",
                                     password=DBPASS,
                                     port="5432")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def insert_player_feature(self, player_feature):
        self.cur.execute(f"INSERT INTO player_features (puuid,match_id,lane,gold_7,gold_15,cs_7,cs_15,xp_7,xp_15,gpm,cspm,xpm,dpm)"
                         f"VALUES ('{player_feature["puuid"]}','{player_feature["match_id"]}','{player_feature["lane"]}','{player_feature["gold_7"]}','{player_feature["gold_15"]}','{player_feature["cs_7"]}','{player_feature["cs_15"]}','{player_feature["xp_7"]}','{player_feature["xp_15"]}','{player_feature["gpm"]}','{player_feature["cspm"]}','{player_feature["xpm"]}','{player_feature["dpm"]}')"
                         f"ON CONFLICT DO NOTHING")
        self.conn.commit()

    def process_timelines(self, count):
        batch_buffer = []
        for subdir, dir, files in os.walk(rootdir):
            for file in files:
                match_id = file.rsplit('_', 1)[0]
                filepath = os.path.join(subdir, file)
                with open(filepath, "r") as f:
                    #patch_version = subdir.rsplit("\\", 1)[1]
                    data = json.load(f)
                    player_features = []
                    puuid_list = data["metadata"]["participants"]
                    frames = data['info']['frames']
                    match_length = len(frames)

                    if match_length < 15:
                        continue

                    frame7 = frames[6]["participantFrames"]
                    frame15 = frames[14]["participantFrames"]
                    last_frame = frames[-1]["participantFrames"]

                    for id in range(1, 11):
                        str_id = str(id)
                        f7 = frame7[str_id]
                        f15 = frame15[str_id]
                        lf = last_frame[str_id]
                        puuid = puuid_list[id - 1]
                        lane = participants.loc[(puuid, match_id), "lane"]
                        batch_buffer.append((
                            puuid, match_id, lane,
                            f7["totalGold"], f15["totalGold"],
                            f7["minionsKilled"] + f7["jungleMinionsKilled"],
                            f15["minionsKilled"] + f15["jungleMinionsKilled"],
                            f7["xp"], f15["xp"],
                            round(lf["totalGold"] / match_length),
                            round((lf["minionsKilled"] + lf["jungleMinionsKilled"]) / match_length),
                            round(lf["xp"] / match_length),
                            round(lf.get("damageStats", {}).get("totalDamageDoneToChampions", 0) / match_length)
                        ))

                if len(batch_buffer) >= 100:
                    self.batch_insert(batch_buffer)
                    count += len(batch_buffer)
                    print(f"inserted {count} players")
                    batch_buffer = []

        if batch_buffer:
            self.batch_insert(batch_buffer)

    def batch_insert(self, data):
        query = """INSERT INTO player_features (puuid, match_id, lane, gold_7, gold_15, cs_7, cs_15, xp_7, xp_15, gpm, cspm, xpm, dpm) 
                    VALUES %s 
                    ON CONFLICT DO NOTHING """
        execute_values(self.cur, query, data)
        self.conn.commit()
timelineProcessor = TimelineProcessor()

timelineProcessor.process_timelines(count)


