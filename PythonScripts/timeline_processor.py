import json
import pandas as pd
import os

rootdir = "C:/Api_Data/combined/timeline_data/EUW"

def process_timelines():

    matches = 0

    for subdir, dir,files in os.walk(rootdir):
        for file in files:
            parts = file.rsplit('_', 1)
            matchId = parts[0]
            filepath = subdir + "/" + file
            with open(filepath, "r") as f:
                patch_version = subdir.rsplit("\\", 1)[1]

                data = json.load(f)

                player_features = []

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
                    player_features.append({
                        "puuid": puuid_list[id - 1],
                        "gold@7": f7["totalGold"],
                        "gold@15": f15["totalGold"],
                        "cs@7": f7["minionsKilled"] + f7["jungleMinionsKilled"],
                        "cs@15": f15["minionsKilled"] + f15["jungleMinionsKilled"],
                        "xp@7": f7["xp"],
                        "xp@15": f15["xp"],
                        "gpm": lf["totalGold"] / match_length,
                        "cspm": (lf["minionsKilled"] + lf["jungleMinionsKilled"]) / match_length,
                        "xpm": lf["xp"] / match_length,
                        "dpm": lf["damageStats"]["totalDamageDoneToChampions"] / match_length,
                    })


process_timelines()

