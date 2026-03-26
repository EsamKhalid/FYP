import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

json_path = '../data/EUW1_7612763297_timeline.json'

rootdir = "C:/Api_Data/combined/timeline_data/EUW"


def process_timelines():
    with open(json_path, 'r') as f:
        data = json.load(f)

    player_features = []

    puuid_list = data["info"]["participants"]

    frames = data['info']['frames']
    frame1 = data["info"]["frames"][0]["participantFrames"]
    frame10 = data["info"]["frames"][10]["participantFrames"]
    frame15 = data["info"]["frames"][15]["participantFrames"]
    last_frame = data["info"]["frames"][-1]["participantFrames"]

    match_length = len(frames)

    for id in range(1, 10):
        player_features.append({
            "puuid": puuid_list[id - 1]["puuid"],
            "gold@10": frame10[str(id)]["totalGold"],
            "gold@15": frame15[str(id)]["totalGold"],
            "cs@10": frame10[str(id)]["minionsKilled"] + frame10[str(id)]["jungleMinionsKilled"],
            "cs@15": frame15[str(id)]["minionsKilled"] + frame15[str(id)]["jungleMinionsKilled"],
            "gpm": last_frame[str(id)]["totalGold"] / match_length,
            "cspm": (last_frame[str(id)]["minionsKilled"] + last_frame[str(id)]["jungleMinionsKilled"]) / match_length,
            "dpm": last_frame[str(id)]["damageStats"]["totalDamageDone"] / match_length,
            "timeEnemyCC": last_frame[str(id)]["timeEnemySpentControlled"],
        })

    def perform_pca():
        df = pd.DataFrame(player_features)

        features = ["gold@10", "gold@15", "cs@10", "cs@15", "gpm", "cspm", "dpm", "timeEnemyCC"]
        scaled = StandardScaler().fit_transform(df[features])

        pca = PCA(n_components=3)
        pca_results = pca.fit_transform(scaled)

        loadings = pd.DataFrame(
            pca.components_.T,
            columns=['PC1', 'PC2', 'PC3'],
            index=features
        )

        print(loadings)

        return [{
            "puuid": df.iloc[i]["puuid"],
            "x": float(pca_results[i, 0]),
            "y": float(pca_results[i, 1]),
            "z": float(pca_results[i, 2])
        } for i in range(len(df))]

    perform_pca()

