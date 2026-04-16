import os
import json

def save_match(match_id, data, directory):

    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(f"{directory}/{match_id}_meta.json", "w") as f:
        json.dump(data, f)

def save_timeline(match_id, data, directory, patch):
    if not os.path.exists(directory + patch):
        os.mkdir(directory + patch)

    with open(f"{directory + patch}/{match_id}_timeline.json", "w") as f:
        json.dump(data, f)


