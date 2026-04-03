import json
import pandas as pd
import os
import psycopg2
from psycopg2.extras import DictCursor

from PythonScripts.creds import DBPASS


rootdir = "C:/Api_Data/combined/timeline_data/EUW"

rawParticipants = pd.read_csv("../data/participants.csv")

participants = pd.DataFrame(rawParticipants.set_index(["puuid", "match_id"])[["lane", "champion_name", "kills", "deaths", "assists", "vision_score"]].to_dict())

class TimelineProcessor():

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
                         f"VALUES ('{player_feature["puuid"]}','{player_feature["match_id"]}','{player_feature["lane"]}','{player_feature["gold_7"]}','{player_feature["gold_15"]}','{player_feature["cs_7"]}','{player_feature["cs_15"]}','{player_feature["xp_7"]}','{player_feature["xp_15"]}','{player_feature["gpm"]}','{player_feature["cspm"]}','{player_feature["xpm"]}','{player_feature["dpm"]}')")
        self.conn.commit()

    def process_timelines(self):

        matches = 0

        for subdir, dir, files in os.walk(rootdir):
            for file in files:
                parts = file.rsplit('_', 1)
                match_id = parts[0]
                filepath = subdir + "/" + file
                with open(filepath, "r") as f:
                    patch_version = subdir.rsplit("\\", 1)[1]

                    data = json.load(f)

                    player_features = []

                    lane = ""

                    puuid_list = data["metadata"]["participants"]

                    frames = data['info']['frames']

                    match_length = len(frames)

                    if match_length < 15:
                        continue

                    frame7 = data["info"]["frames"][6]["participantFrames"]
                    frame15 = data["info"]["frames"][14]["participantFrames"]
                    last_frame = data["info"]["frames"][-1]["participantFrames"]

                    for id in range(1, 11):
                        f7 = frame7[str(id)]
                        f15 = frame15[str(id)]
                        lf = last_frame[str(id)]
                        puuid = puuid_list[id - 1]
                        player_features.append({
                            "puuid": puuid,
                            "match_id" : match_id,
                            "lane" : participants.loc[(puuid, match_id), "lane"],
                            "gold_7": f7["totalGold"],
                            "gold_15": f15["totalGold"],
                            "cs_7": f7["minionsKilled"] + f7["jungleMinionsKilled"],
                            "cs_15": f15["minionsKilled"] + f15["jungleMinionsKilled"],
                            "xp_7": f7["xp"],
                            "xp_15": f15["xp"],
                            "gpm": round(lf["totalGold"] / match_length),
                            "cspm": round((lf["minionsKilled"] + lf["jungleMinionsKilled"]) / match_length),
                            "xpm": round(lf["xp"] / match_length),
                            "dpm": round(lf["damageStats"]["totalDamageDoneToChampions"] / match_length),
                        })
                self.insert_player_feature(player_features[0])
                exit()

timelineProcessor = TimelineProcessor()

timelineProcessor.process_timelines()


