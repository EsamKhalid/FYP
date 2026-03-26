import json
import pandas

json_path = '../data/EUW1_7612763297_timeline.json'



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

def calculate_movement():

    pass

for id in range(1,10):
    player_features.append({
        "puuid" : puuid_list[id - 1]["puuid"],
        "gold@10" : frame10[str(id)]["totalGold"],
        "gold@15" : frame15[str(id)]["totalGold"],
        "cs@10" : frame10[str(id)]["minionsKilled"] + frame10[str(id)]["jungleMinionsKilled"],
        "cs@15" : frame15[str(id)]["minionsKilled"] + frame15[str(id)]["jungleMinionsKilled"],
        "gpm" : last_frame[str(id)]["totalGold"] / match_length,
        "cspm" : (last_frame[str(id)]["minionsKilled"] + last_frame[str(id)]["jungleMinionsKilled"]) / match_length,
        "dpm" : last_frame[str(id)]["damageStats"]["totalDamageDone"] / match_length,
        "timeEnemyCC" : last_frame[str(id)]["timeEnemySpentControlled"],
    })


print(player_features)

print(json.dumps(frame10, indent=4))


