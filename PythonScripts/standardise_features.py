import psycopg2
from psycopg2.extras import DictCursor, execute_values
import pandas as pd
from sklearn.preprocessing import StandardScaler

from PythonScripts.creds import DBPASS

class Standardiser:

    def __init__(self):
        self.conn = psycopg2.connect(database="features_db",
                                     user="postgres",
                                     host="localhost",
                                     password=DBPASS,
                                     port="5432")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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


standardiser = Standardiser()

df = standardiser.fetch_table()
standardiser.standardise(df)