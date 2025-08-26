import os
import json

def save_match(match_id, data, directory):
    with open(f"{directory}/{match_id}_meta.json", "w") as f:
        json.dump(data,f)