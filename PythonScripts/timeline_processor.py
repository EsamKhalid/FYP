import json
import pandas as pd
import os
import psycopg2
from psycopg2.extras import DictCursor, execute_values

from sklearn.preprocessing import StandardScaler

from PythonScripts.creds import DBPASS

import math


rootdir = "C:/Api_Data/combined/timeline_data/EUW"

rawParticipants = pd.read_csv("../data/participants.csv")

participants = pd.DataFrame(rawParticipants.set_index(["puuid", "match_id"])[["lane", "champion_name", "kills", "deaths", "assists", "vision_score", "team_id", "kill_participation", "turret_damage", "objective_damage"]].to_dict())

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
                with (open(filepath, "r") as f):
                    #patch_version = subdir.rsplit("\\", 1)[1]
                    data = json.load(f)
                    puuid_list = data["metadata"]["participants"]

                    frames = data['info']['frames']
                    match_length = len(frames)

                    if match_length < 15:
                        continue

                    frame7 = frames[6]["participantFrames"]
                    frame15 = frames[14]["participantFrames"]
                    last_frame = frames[-1]["participantFrames"]

                    winning_team = None

                    winning_team = frames[-1]["events"][-1]["winningTeam"]


                    all_participant_frames = []

                    for frame in frames:
                        all_participant_frames.append(frame["participantFrames"])

                    for id in range(1, 11):
                        str_id = str(id)
                        f7 = frame7[str_id]
                        f15 = frame15[str_id]
                        lf = last_frame[str_id]

                        puuid = puuid_list[id - 1]

                        lane, team_id, kills, deaths, assists, vision_score, kill_participation, turret_damage, objective_damage  = participants.loc[(puuid, match_id), ["lane", "team_id", "kills", "deaths", "assists", "vision_score", "kill_participation", "turret_damage", "objective_damage"]]

                        team_id = str(team_id)
                        kills = int(kills)
                        deaths = int(deaths)
                        assists = int(assists)
                        vision_score = int(vision_score)
                        kill_participation = float(kill_participation)
                        turret_damage = int(turret_damage)
                        objective_damage = int(objective_damage)

                        if team_id == winning_team:
                            win = True
                        else:
                            win = False

                        if(kills or assists) > 0:
                            if deaths == 0:
                                kda = (kills + assists) / 1
                            else:
                                kda = (kills + assists) / deaths
                        else:
                            kda = 0

                        total_gold = lf["totalGold"]
                        total_cs = lf["minionsKilled"] + lf["jungleMinionsKilled"]
                        total_xp = lf["xp"]
                        total_damage = lf["damageStats"]["totalDamageDoneToChampions"]
                        total_damage_taken = lf["damageStats"]["totalDamageTaken"]
                        cc_score = lf["timeEnemySpentControlled"]

                        pre_15_roaming = 0
                        total_roaming = 0

                        for i in range(0,match_length - 1):
                            current_position = all_participant_frames[i][str_id]["position"]
                            next_position = all_participant_frames[i + 1][str_id]["position"]
                            delta_x = (next_position["x"] - current_position["x"]) ** 2
                            delta_y = (next_position["y"] - current_position["y"]) ** 2
                            delta_pos = math.sqrt(delta_x + delta_y)
                            if i < 14:
                                pre_15_roaming += delta_pos
                            total_roaming += delta_pos

                        batch_buffer.append((
                            puuid,
                            match_id,
                            lane,
                            f7["totalGold"], f15["totalGold"],
                            f7["minionsKilled"] + f7["jungleMinionsKilled"],
                            f15["minionsKilled"] + f15["jungleMinionsKilled"],
                            f7["xp"], f15["xp"],
                            f7["damageStats"]["totalDamageDoneToChampions"], f15["damageStats"]["totalDamageDoneToChampions"],
                            round(pre_15_roaming),
                            total_gold,
                            total_cs,
                            total_xp,
                            total_damage,
                            lf["damageStats"]["totalDamageTaken"],
                            round(total_gold / match_length),
                            round(total_cs / match_length),
                            round(total_xp / match_length),
                            round(total_damage / match_length),
                            kda,
                            kill_participation,
                            cc_score,
                            vision_score,
                            turret_damage,
                            objective_damage,
                            round(total_roaming),
                            win
                        ))

                if len(batch_buffer) >= 100:
                    self.batch_insert(batch_buffer)
                    count += len(batch_buffer)
                    print(f"inserted {count} players")
                    batch_buffer = []

        if batch_buffer:
            self.batch_insert(batch_buffer)

    def batch_insert(self, data):
        query = """INSERT INTO player_features (puuid, match_id, lane, gold_7, gold_15, cs_7, cs_15, xp_7, xp_15, damage_7, damage_15, roaming_15, total_gold, total_cs, total_xp, total_damage, total_damage_taken, gpm, cspm, xpm, dpm, kda, kill_participation, cc_score, vision_score, turret_damage, objective_damage, total_roaming_distance, win) 
                    VALUES %s 
                    ON CONFLICT DO NOTHING """
        execute_values(self.cur, query, data)
        self.conn.commit()

    def fetch_table(self):
        self.cur.execute("SELECT * FROM player_features")
        return pd.DataFrame(self.cur.fetchall())

    def standardise(self,df):
        features = [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'gpm', 'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15', 'total_gold', 'total_cs', 'total_xp',
            'total_damage', 'kda', 'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ]

        for lane in df['lane'].unique():
            df_lane_subset = df[df['lane'] == lane].copy()

            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df_lane_subset[features])

            df_lane_subset[features] = scaled_data

            db_columns = [
                'puuid', 'match_id', 'lane', 'win', 'gold_7', 'gold_15', 'cs_7', 'cs_15',
                'xp_7', 'xp_15', 'damage_7', 'damage_15', 'roaming_15', 'gpm', 'cspm',
                'xpm', 'dpm', 'total_gold', 'total_cs', 'total_xp', 'total_damage',
                'total_damage_taken', 'total_roaming_distance', 'kda',
                'kill_participation', 'cc_score', 'vision_score', 'turret_damage',
                'objective_damage'
            ]

            self.db_insert(df_lane_subset[db_columns])
            print(f"inserted '{lane}'")

    def db_insert(self, insert_df):
        query = "INSERT INTO player_standardised (puuid, match_id, lane, win, gold_7, gold_15, cs_7, cs_15, xp_7, xp_15, damage_7, damage_15, roaming_15, gpm, cspm, xpm, dpm, total_gold, total_cs, total_xp, total_damage,total_damage_taken, total_roaming_distance, kda, kill_participation, cc_score, vision_score, turret_damage, objective_damage) VALUES %s ON CONFLICT DO NOTHING"
        tuples = [tuple(x) for x in insert_df.to_numpy()]
        execute_values(self.cur, query, tuples)
        self.conn.commit()


timelineProcessor = TimelineProcessor()



