import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import psycopg2
from psycopg2.extras import DictCursor, execute_values

import matplotlib.cm as cm

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import FeatureAgglomeration, KMeans, HDBSCAN
from sklearn.metrics import silhouette_samples, silhouette_score
from statsmodels.stats.outliers_influence import variance_inflation_factor

import umap
import hdbscan

import joblib

from creds import DBPASS

import math

rootdir = "C:/Api_Data/combined/timeline_data/EUW"

class TimelineProcessor:

    def __init__(self):
        self.conn = psycopg2.connect(database="features_db",
                                     user="postgres",
                                     host="localhost",
                                     password=DBPASS,
                                     port="5432")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.features = [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'gpm', 'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15', 'total_gold', 'total_cs', 'total_xp',
            'total_damage', 'kda', 'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ]
        self.reduced_features = {"TOP" : [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15','kda',
            'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ],
        "JUNGLE" :            [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_15',
            'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15','kda',
            'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ],
        "MIDDLE" :             [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15','kda',
            'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ],
        "BOTTOM" :            [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15','kda',
            'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ],
        "UTILITY" :            [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15','kda',
            'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ]
        }



    def close_connection(self):
        self.cur.close()
        self.conn.close()

    def read_participants(self):
        rawParticipants = pd.read_csv("../data/participants.csv")

        participants = pd.DataFrame(rawParticipants.set_index(["puuid", "match_id"])[
                                        ["lane", "champion_name", "kills", "deaths", "assists", "vision_score",
                                         "team_id", "kill_participation", "turret_damage",
                                         "objective_damage"]].to_dict())

        return participants

    def read_players(self):
        players = pd.read_csv("../data/player_ranks.csv")
        players = pd.DataFrame(players.set_index("puuid")["current_rank"].to_dict())
        return players

    def insert_player_feature(self, player_feature):
        self.cur.execute(f"INSERT INTO player_features (puuid,match_id,lane,gold_7,gold_15,cs_7,cs_15,xp_7,xp_15,gpm,cspm,xpm,dpm)"
                         f"VALUES ('{player_feature["puuid"]}','{player_feature["match_id"]}','{player_feature["lane"]}','{player_feature["gold_7"]}','{player_feature["gold_15"]}','{player_feature["cs_7"]}','{player_feature["cs_15"]}','{player_feature["xp_7"]}','{player_feature["xp_15"]}','{player_feature["gpm"]}','{player_feature["cspm"]}','{player_feature["xpm"]}','{player_feature["dpm"]}')"
                         f"ON CONFLICT DO NOTHING")
        self.conn.commit()

    def process_timelines(self, count):
        participants = self.read_participants()
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
            self.insert_features(batch_buffer)

    def insert_features(self, data):
        query = """INSERT INTO player_features (puuid, match_id, lane, gold_7, gold_15, cs_7, cs_15, xp_7, xp_15, damage_7, damage_15, roaming_15, total_gold, total_cs, total_xp, total_damage, total_damage_taken, gpm, cspm, xpm, dpm, kda, kill_participation, cc_score, vision_score, turret_damage, objective_damage, total_roaming_distance, win) 
                    VALUES %s 
                    ON CONFLICT DO NOTHING """
        execute_values(self.cur, query, data)
        self.conn.commit()

    def fetch_table(self, table_name):
        self.cur.execute(f"SELECT * FROM {table_name}")
        return pd.DataFrame(self.cur.fetchall())

    def standardise(self):

        df = self.fetch_table("player_features")

        for lane in df['lane'].unique():
            features = self.features
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
            joblib.dump(scaler  , f"scaler_{lane}")
            self.insert_standardised(df_lane_subset[db_columns])
            print(f"inserted '{lane}'")

    def insert_standardised(self, insert_df):
        query = "INSERT INTO player_standardised (puuid, match_id, lane, win, gold_7, gold_15, cs_7, cs_15, xp_7, xp_15, damage_7, damage_15, roaming_15, gpm, cspm, xpm, dpm, total_gold, total_cs, total_xp, total_damage,total_damage_taken, total_roaming_distance, kda, kill_participation, cc_score, vision_score, turret_damage, objective_damage) VALUES %s ON CONFLICT DO NOTHING"
        tuples = [tuple(x) for x in insert_df.to_numpy()]
        execute_values(self.cur, query, tuples)
        self.conn.commit()

    def remove_collinear_features(self):
        standardised_df = self.fetch_table("player_standardised")

        for lane in standardised_df['lane'].unique():
            standardised_lane_subset = standardised_df[standardised_df['lane'] == lane][self.features]
            correlation_matrix = standardised_lane_subset.corr().abs()
            plt.figure(figsize=(16, 12))
            plt.title(f"Correlation Matrix {lane}")
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
            plt.savefig(f"../figures/correlation_matrices/Correlation_Matrix_{lane}.png", dpi=150)
            plt.show()
            upper = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))
            to_drop = [column for column in upper.columns if any(upper[column] > 0.90)]
            print(to_drop, lane)

    def remove_high_vif_features(self):
        threshold = 10
        standardised_df = self.fetch_table("player_standardised")

        for lane in standardised_df['lane'].unique():
            reduced_lane_subset = standardised_df[self.reduced_features[lane]]
            vif_data = pd.DataFrame()
            vif_data["feature"] = reduced_lane_subset.columns

            vif_data["VIF"] = [variance_inflation_factor(reduced_lane_subset.values, i)
                               for i in range(len(reduced_lane_subset.columns))]

            vif_data = vif_data.sort_values("VIF", ascending=True)

            plt.figure(figsize=(10, 6))

            colors = ['skyblue' if x < 10 else 'tomato' for x in vif_data['VIF']]

            plt.barh(vif_data["feature"], vif_data["VIF"], color=colors)

            plt.axvline(x=threshold, color='red', linestyle='--', label='Threshold (10)')

            plt.title(f"VIF Scores - Lane: {lane}")
            plt.xlabel("VIF Value")
            plt.ylabel("Features")
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"../figures/VIF Plots/VIF_{lane}.png", dpi=150)
            plt.show()


    def apply_pca(self):
        standardised_df = self.fetch_table("player_standardised")

        for lane in standardised_df['lane'].unique():
            standardised_lane_subset = standardised_df[standardised_df['lane'] == lane].copy()
            pca = PCA(n_components=3, random_state=4)
            pca_results = pca.fit_transform(standardised_lane_subset[self.reduced_features[lane]])

            explained_variance = pca.explained_variance_ratio_
            total_info = explained_variance.sum()

            print(f"Lane: {lane}")
            print(f"  x explains: {explained_variance[0]:.1%}")
            print(f"  y explains: {explained_variance[1]:.1%}")
            print(f"  z explains: {explained_variance[2]:.1%}")
            print(f"  retained: {total_info:.1%}")

            standardised_lane_subset[['x', 'y', 'z']] = pca_results
            self.insert_reduced_features(standardised_lane_subset, "player_pca")

    def apply_fa(self):
        standardised_df = self.fetch_table("player_standardised")

        for lane in standardised_df['lane'].unique():
            standardised_lane_subset = standardised_df[standardised_df['lane'] == lane].copy()
            agglo = FeatureAgglomeration(n_clusters=3)
            agglomeration_results = agglo.fit_transform(standardised_lane_subset[self.reduced_features[lane]])

            feature_groups = pd.DataFrame({
                'feature': self.reduced_features[lane],
                'group': agglo.labels_
            }).sort_values('group')

            print(feature_groups)

            standardised_lane_subset[['x', 'y', 'z']] = agglomeration_results
            self.insert_reduced_features(standardised_lane_subset, "player_fa")
            print("Inserted " + lane)

    def apply_umap(self, table):
        standardised_df = self.fetch_table("player_standardised")

        neighbours = {"TOP" : 10, "JUNGLE" : 15, "MIDDLE" : 15, "BOTTOM" : 30, "UTILITY" : 50}

        for lane in standardised_df['lane'].unique():
            if lane == "TOP" or lane == "MIDDLE":
                features = self.reduced_features[lane]
            else:
                features = self.features
            standardised_lane_subset = standardised_df[standardised_df['lane'] == lane].copy()
            umap_3d = umap.UMAP(n_components=3,n_neighbors=neighbours[lane], min_dist=0.0 ,random_state=4)
            umap_results = umap_3d.fit_transform(standardised_lane_subset[features])
            joblib.dump(umap_results, f"umap_standard_{lane}.sav")
            standardised_lane_subset[['x', 'y', 'z']] = umap_results
            self.insert_reduced_features(standardised_lane_subset, table)

    def insert_reduced_features(self, insert_df, table):
        insert_df = insert_df[['puuid', 'match_id', 'lane', 'win', 'x', 'y', 'z']]
        query = f"INSERT INTO {table} (puuid, match_id, lane, win, x, y, z) VALUES %s ON CONFLICT (puuid, match_id) DO UPDATE SET x = EXCLUDED.x, y = EXCLUDED.y, z = EXCLUDED.z;"
        tuples = [tuple(x) for x in insert_df.to_numpy()]
        execute_values(self.cur, query, tuples)
        self.conn.commit()

    def tune_table_hdbscan_params(self, table):
        umap_df = self.fetch_table(table)

        min_cluster_sizes = [10, 15, 25, 30, 40, 50, 75, 100, 150, 200]
        min_samples = [1,5,10]

        for lane in umap_df['lane'].unique():
            lane_subset = umap_df[umap_df['lane'] == lane].copy()
            lane_coordinates = lane_subset[['x', 'y', 'z']]

            best_validity = -1.0
            best_size = None
            best_clusters = None
            best_sample = None

            for size in min_cluster_sizes:
                for min_sample in min_samples:
                    clusterer = hdbscan.HDBSCAN(min_cluster_size=size, min_samples=min_sample ,gen_min_span_tree=True)
                    clusters = clusterer.fit_predict(lane_coordinates)

                    relative_validity = clusterer.relative_validity_

                    if relative_validity > best_validity:
                        best_validity = relative_validity
                        best_clusters = len(np.unique(clusters)) - (1 if -1 in clusters else 0)
                        best_size = size
                        best_sample = min_sample

            print(f"Lane : {lane} | best size : {best_size} | best sample : {best_sample} | relative validity : {best_validity:.4f}")
            print(f"Clusters: {best_clusters} | Noise: {list(clusters).count(-1)}")

    def tune_df_hdbscan_params(self, df, lane):
        min_cluster_sizes = [10, 15, 25, 30, 40, 50, 75, 100, 150, 200]
        min_samples = [1, 5, 10]

        lane_coordinates = df[['x', 'y', 'z']]

        best_validity = -1.0
        best_size = None
        best_clusters = None
        best_sample = None

        for size in min_cluster_sizes:
            for min_sample in min_samples:
                clusterer = hdbscan.HDBSCAN(min_cluster_size=size, min_samples=min_sample, gen_min_span_tree=True)
                clusters = clusterer.fit_predict(lane_coordinates)

                relative_validity = clusterer.relative_validity_

                if relative_validity > best_validity:
                    best_validity = relative_validity
                    best_clusters = len(np.unique(clusters)) - (1 if -1 in clusters else 0)
                    best_size = size
                    best_sample = min_sample
        print(f"Lane : {lane} | best size : {best_size} | best sample : {best_sample} | relative validity : {best_validity:.4f}")
        print(f"Clusters: {best_clusters} | Noise: {list(clusters).count(-1)}")




    def apply_hdbscan(self):
        umap_df = self.fetch_table("player_umap_standard")
        #reduced_df = self.fetch_table("player_umap_reduced")

        cluster_sizes = {"TOP" : 5, "JUNGLE" : 10, "MIDDLE" : 100, "BOTTOM" : 40, "UTILITY" : 75}
        min_samples = {"TOP" : 1, "JUNGLE" : 1, "MIDDLE" : 5, "BOTTOM" : 1, "UTILITY" : 10}

        for lane in umap_df['lane'].unique():
            # if lane == "TOP" or lane == "MIDDLE":
            #     lane_subset = reduced_df[reduced_df['lane'] == lane].copy()
            # else:
            #     lane_subset = umap_df[umap_df['lane'] == lane].copy()
            lane_subset = umap_df[umap_df['lane'] == lane].copy()
            lane_coordinates = lane_subset[['x', 'y', 'z']]

            clusterer = hdbscan.HDBSCAN(min_cluster_size=cluster_sizes[lane],min_samples=min_samples[lane], gen_min_span_tree=True, prediction_data=True)
            joblib.dump(clusterer, f"hdbscan_standard_{lane}.sav")
            clusters = clusterer.fit_predict(lane_coordinates)
            unique_clusters = np.unique(clusters)
            n_clusters = len(unique_clusters) - (1 if -1 in clusters else 0)
            n_noise = list(clusters).count(-1)

            print(f"number of clusters: {n_clusters}")
            print(f"number of noise points: {n_noise} (out of {len(clusters)})")
            print(f"relative validity: {clusterer.relative_validity_}")

            lane_subset['cluster'] = clusters

            self.insert_clusters("player_umap_standard", lane_subset)
            print(f"inserted {lane}")


    def insert_clusters(self, table, cluster_df):
        query = f"INSERT INTO {table} (puuid, match_id, lane, win, x, y, z, cluster, current_rank) VALUES %s ON CONFLICT (match_id, puuid) DO UPDATE SET cluster = EXCLUDED.cluster"
        tuples = [tuple(x) for x in cluster_df.to_numpy()]
        execute_values(self.cur, query, tuples)
        self.conn.commit()

    def calculate_optimal_k(self, table, feature_state):
        df = self.fetch_table(table)

        range_num_k = range(2, 11)

        for lane in df['lane'].unique():
            if table == "player_pca" or table == "player_fa" or table == "player_umap":
                lane_subset = df[df['lane'] == lane][['x', 'y', 'z']]
            else:
                lane_subset = df[df['lane'] == lane][self.features]

            silhouette_scores = []

            for k in range_num_k:
                km = KMeans(n_clusters=k, random_state=4, n_init=10)
                labels = km.fit_predict(lane_subset)
                score = silhouette_score(lane_subset, labels, sample_size=1000, random_state=4)
                silhouette_scores.append(score)

            plt.figure(figsize=(8, 4))
            plt.plot(list(range_num_k), silhouette_scores, marker='o', color='steelblue')
            plt.xlabel("Number of Clusters (k)")
            plt.ylabel("Silhouette Score")
            plt.title(f"{lane} Silhouette Score {table}")
            plt.xticks(range(2, 11))
            plt.tight_layout()
            plt.savefig(f"../figures/{lane}_{table}_{feature_state}.png", dpi=150)
            plt.show()

    def tune_umap(self):
        standardised_df = self.fetch_table("player_standardised")
        neighbours = [10, 15, 20, 30, 50]

        lanes = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

        for neighbour in neighbours:
            for lane in lanes:
                print(lane, neighbour)
                if lane == "TOP" or lane == "MIDDLE":
                    features = self.reduced_features[lane]
                else:
                    features = self.features
                standardised_lane_subset = standardised_df[standardised_df['lane'] == lane].copy()
                umap_3d = umap.UMAP(n_components=3, n_neighbors=neighbour, min_dist=0.0, random_state=4)
                umap_results = umap_3d.fit_transform(standardised_lane_subset[features])
                standardised_lane_subset[['x', 'y', 'z']] = umap_results
                self.tune_df_hdbscan_params(standardised_lane_subset, lane)




timelineProcessor = TimelineProcessor()
#timelineProcessor.apply_umap("player_umap_standard")
# timelineProcessor.apply_hdbscan()
timelineProcessor.standardise()