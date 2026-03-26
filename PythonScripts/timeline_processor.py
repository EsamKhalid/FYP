import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

json_path = '../data/EUW1_7612763297_timeline.json'

rootdir = "C:/Api_Data/combined/timeline_data/EUW"


def process_timelines():

    matches = 0

    for subdir, dir,files in os.walk(rootdir):
        for file in files:
            parts = file.rsplit('_', 1)
            matchId = parts[0]
            filepath = subdir + "/" + file
            with open(filepath, "r") as f:

                data = json.load(f)

                player_features = []

                puuid_list = data["metadata"]["participants"]

                frames = data['info']['frames']

                match_length = len(frames)


                if match_length < 15:
                    break

                frame1 = data["info"]["frames"][0]["participantFrames"]
                frame10 = data["info"]["frames"][9]["participantFrames"]
                frame15 = data["info"]["frames"][14]["participantFrames"]
                last_frame = data["info"]["frames"][-1]["participantFrames"]





                for id in range(1, 11):
                    f10 = frame10[str(id)]
                    f15 = frame15[str(id)]
                    lf = last_frame[str(id)]
                    player_features.append({
                        "puuid": puuid_list[id - 1],
                        "gold@10": f10["totalGold"],
                        "gold@15": f15["totalGold"],
                        "cs@10": f10["minionsKilled"] + f10["jungleMinionsKilled"],
                        "cs@15": f15["minionsKilled"] + f15["jungleMinionsKilled"],
                        "xp@10": f10["xp"],
                        "xp@15": f15["xp"],
                        "gpm": lf["totalGold"] / match_length,
                        "cspm": (lf["minionsKilled"] + lf["jungleMinionsKilled"]) / match_length,
                        "xpm": lf["xp"] / match_length,
                        "dpm": lf["damageStats"]["totalDamageDoneToChampions"] / match_length,
                        "timeEnemyCC": lf["timeEnemySpentControlled"],
                    })

                def perform_pca():
                    df = pd.DataFrame(player_features)
                    features = ["gold@10", "gold@15", "cs@10", "cs@15","xp@10", "xp@15", "gpm", "cspm", "xpm", "dpm", "timeEnemyCC"]
                    scaled = StandardScaler().fit_transform(df[features])

                    pca = PCA(n_components=3)
                    pca_results = pca.fit_transform(scaled)


                    return [{
                        "puuid": puuid_list[i],
                        "match_id" : matchId,
                        "x": float(pca_results[i, 0]),
                        "y": float(pca_results[i, 1]),
                        "z": float(pca_results[i, 2])
                    } for i in range(len(df))]



                df = pd.DataFrame(perform_pca())
                df.to_csv('../data/CSV/PCACoords.csv', mode='a', header=not os.path.exists('../data/CSV/PCACoords.csv'), index=False)
                matches +=1
                print("written " + str(matches) + " matches")


process_timelines()

# loadings = pd.DataFrame(
#     pca.components_.T,
#     columns=['PC1', 'PC2', 'PC3'],
#     index=features
# )



