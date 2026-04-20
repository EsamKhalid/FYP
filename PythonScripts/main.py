import json
from http.client import responses
from tkinter.ttk import Label

from fastapi import FastAPI
import requests
from creds import API_KEY
from creds import DBPASS
import time

import pandas as pd

import psycopg2
from psycopg2.extras import DictCursor, execute_values

import math

import joblib

import hdbscan
app = FastAPI()

conn = psycopg2.connect(database="features_db",
                        user="postgres",
                        host="localhost",
                        password=DBPASS,
                        port="5432")

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

standard_features = ['gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'gpm', 'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15', 'total_gold', 'total_cs', 'total_xp',
            'total_damage', 'kda', 'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken']

feature_list = {"TOP" : [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15','kda',
            'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ],
        "JUNGLE" :            [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'gpm', 'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15', 'total_gold', 'total_cs', 'total_xp',
            'total_damage', 'kda', 'kill_participation', 'cc_score',
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
            'gpm', 'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15', 'total_gold', 'total_cs', 'total_xp',
            'total_damage', 'kda', 'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ],
        "UTILITY" :            [
            'gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15',
            'gpm', 'cspm', 'xpm', 'dpm', 'damage_7', 'damage_15',
            'roaming_15', 'total_gold', 'total_cs', 'total_xp',
            'total_damage', 'kda', 'kill_participation', 'cc_score',
            'vision_score', 'turret_damage', 'objective_damage',
            'total_roaming_distance', 'total_damage_taken'
        ]
        }

def api_call(url: str, max_retries=3) -> json:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={"X-Riot-Token" : API_KEY}, timeout=10)
            if response.status_code == 200:
                time.sleep(0.2)
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After'), 60)
                print(f"Rate limited, waiting {retry_after} seconds")
                time.sleep(retry_after + 120)
            elif response.status_code == 404:
                return None
            else:
                print(f"API error {response.status_code}")
                time.sleep(2 ** attempt)

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(2 ** attempt)
    return None

def load_models(lane):
    scaler = joblib.load(f"../Models/scaler_{lane}.sav")
    umap_model = joblib.load(f"../Models/umap_standard_{lane}.sav")
    hdbscan_model = joblib.load(f"../Models/hdbscan_standard_{lane}.sav")

    return scaler, umap_model, hdbscan_model


def get_puuid(name : str, tag : str) -> str:
    response = api_call(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}")
    print(response["puuid"])
    return response["puuid"]

def get_matches(puuid : str):
    response = api_call(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&type=ranked&start=0&count=100")
    return response

def get_match_data(match_id):
    response = api_call(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}")
    return response

def get_timeline_data(match_id):
    response = api_call(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline")
    return response

def get_player_rank(puuid):
    response = api_call(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}")

    if not response:
        return

    if len(response) > 1:
        if response[0]["queueType"] == "RANKED_SOLO_5x5":
            return response[0]["tier"]
        else:
            return response[1]["tier"]
    else:
        return response[0]["tier"]

def get_player_data(puuid, lane):
    cur.execute(f"SELECT * FROM player_umap_standard WHERE puuid = '{puuid}' and lane = '{lane}'")
    return cur.fetchall()

def process_player(name, tag, lane):
    print(f"Processing player: {name} #{tag}")
    puuid = get_puuid(name, tag)
    rank = get_player_rank(puuid)
    if not rank:
        return False, "Not currently ranked", puuid
    player_data = get_player_data(puuid, lane)
    if player_data:
        return True, "None", puuid
    match_count = 0
    match_list = get_matches(puuid)
    for match_id in match_list:
        if match_count >= 20:
            return True, "None", puuid
        print(f"processing: {match_id}")
        if process_match(match_id, puuid, lane, rank):
            match_count += 1
    return True, "None", puuid


def insert_features(data):
    query = """INSERT INTO player_features (puuid, match_id, lane,rank, gold_7, gold_15, cs_7, cs_15, xp_7, xp_15, damage_7, damage_15, roaming_15, total_gold, total_cs, total_xp, total_damage, total_damage_taken, gpm, cspm, xpm, dpm, kda, kill_participation, cc_score, vision_score, turret_damage, objective_damage, total_roaming_distance, win) 
                VALUES %s 
                ON CONFLICT DO NOTHING """
    execute_values(cur, query, data)
    conn.commit()

def insert_coord_cluster(data):
    query = f"INSERT INTO player_umap_standard (puuid, match_id, lane, win, x, y, z, cluster, current_rank) VALUES %s ON CONFLICT (match_id, puuid) DO UPDATE SET cluster = EXCLUDED.cluster"
    tuples = [tuple(x) for x in data.to_numpy()]
    execute_values(cur, query, tuples)
    conn.commit()

def get_features(puuid, match_id):
    cur.execute(f"SELECT * FROM player_features WHERE puuid='{puuid}' AND match_id='{match_id}'")
    return pd.DataFrame(cur.fetchall())

def process_match(match_id, puuid, lane, rank):
    raw_match_data = get_match_data(match_id)
    match_data = raw_match_data["info"]
    if match_data["queueId"] != 420:
        return False

    if match_data["gameDuration"] < 900:
        return False

    timeline_data = get_timeline_data(match_id)
    features = []

    participants_list = raw_match_data["metadata"]["participants"]
    pos = participants_list.index(puuid)


    participants = raw_match_data["info"]["participants"]

    team_kills = {}

    for participant in participants:
        team_id = participant["teamId"]
        team_kills[team_id] = team_kills.get(team_id, 0) + participant["kills"]

    player_data = participants[pos]
    player_lane = player_data["individualPosition"]

    if player_lane != lane:
        return False

    challenges = player_data["challenges"]

    dpm = round(challenges["damagePerMinute"])
    gpm = round(challenges["goldPerMinute"])
    kda = challenges["kda"]

    kp = round(player_data["kills"] / max(team_kills[player_data["teamId"]], 1),2)
    objective_damage = player_data["damageDealtToObjectives"]
    turret_damage = player_data["damageDealtToTurrets"]
    total_gold = player_data["goldEarned"]
    total_damage = player_data["totalDamageDealtToChampions"]
    total_damage_taken = player_data["totalDamageTaken"]
    vision_score = player_data["visionScore"]
    win = player_data["win"]

    timeline_participants = timeline_data["metadata"]["participants"]
    timeline_pos = timeline_participants.index(puuid) + 1

    frames = timeline_data["info"]["frames"]

    player_frames = []

    for frame in frames:
        player_frames.append(frame["participantFrames"][str(timeline_pos)])

    match_length = len(player_frames)
    frame7 = player_frames[6]
    frame15 = player_frames[14]
    last_frame = player_frames[-1]

    total_cs = last_frame["minionsKilled"] + last_frame["jungleMinionsKilled"]
    total_xp = last_frame["xp"]
    cc_score = last_frame["timeEnemySpentControlled"]

    pre_15_roaming = 0
    total_roaming = 0

    for i in range(0, match_length - 1):
        current_position = player_frames[i]["position"]
        next_position = player_frames[i + 1]["position"]
        delta_x = (next_position["x"] - current_position["x"]) ** 2
        delta_y = (next_position["y"] - current_position["y"]) ** 2
        delta_pos = math.sqrt(delta_x + delta_y)
        if i < 14:
            pre_15_roaming += delta_pos
        total_roaming += delta_pos

    features.append((
        puuid,
        match_id,
        player_lane,
        rank,
        frame7["totalGold"], frame15["totalGold"],
        frame7["minionsKilled"] + frame7["jungleMinionsKilled"],
        frame15["minionsKilled"] + frame15["jungleMinionsKilled"],
        frame7["xp"], frame15["xp"],
        frame7["damageStats"]["totalDamageDoneToChampions"], frame15["damageStats"]["totalDamageDoneToChampions"],
        round(pre_15_roaming),
        total_gold,
        total_cs,
        total_xp,
        total_damage,
        total_damage_taken,
        gpm,
        round(total_cs / match_length),
        round(total_xp / match_length),
        dpm,
        kda,
        kp,
        cc_score,
        vision_score,
        turret_damage,
        objective_damage,
        round(total_roaming),
        win
    ))

    insert_features(features)

    scaler, umap_model, hdbscan_model = load_models(lane)

    feature_df = get_features(puuid, match_id)

    standardised = scaler.transform(feature_df[standard_features])

    reduced = umap_model.transform(standardised)

    cluster, probability = hdbscan.approximate_predict(hdbscan_model, reduced)

    reduced = reduced.flatten().tolist()

    df_list = []

    df_list.append((
        puuid,
        match_id,
        lane,
        win,
        reduced[0],
        reduced[1],
        reduced[2],
        cluster[0],
        rank
    ))

    df = pd.DataFrame(df_list)

    insert_coord_cluster(df)#

    return True

#print(process_player("SpilltTea", "TEA", "MIDDLE"))

@app.get("/getPlayer/{name}/{tag}/{lane}")

def get_player(name, tag, lane):

    player_points = None
    points = None

    success, error, puuid = process_player(name, tag, lane)
    if success:
        player_points = get_player_data(puuid, lane)
        cur.execute(f"SELECT * FROM player_umap_final WHERE lane = '{lane}' AND cluster != -1 AND puuid != '{puuid}'")
        points = cur.fetchall()



    # Add a boolean to determine if the fetch was successful or not

    return {
        "playerPoints" : player_points,
        "points" : points,
        "success" : success,
        "error" : error
    }

# @app.get("/clusterManager/{name}/{tag}")
#
# def get_player(name : str, tag : str):
#
#     puuid = get_puuid(name, tag)
#     matchList = get_matches(puuid)
#     points = process_matches(matchList, puuid)
#
#     return {
#         "puuid" : puuid,
#         "points" : points,
#     }

@app.get("/UMAPPoints/{lane}")

def get_points(lane : str):
    cur.execute(f"SELECT * FROM player_umap_standard WHERE lane = '{lane}' AND cluster != -1")
    points = cur.fetchall()

    df = pd.DataFrame(points)

    return {
        "UMAPPoints" : points
    }
