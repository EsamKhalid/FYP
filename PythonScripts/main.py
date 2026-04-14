import json
from http.client import responses

from fastapi import FastAPI
import requests
from creds import API_KEY
from creds import DBPASS
import time

import pandas as pd

import psycopg2
from psycopg2.extras import DictCursor
app = FastAPI()

conn = psycopg2.connect(database="features_db",
                        user="postgres",
                        host="localhost",
                        password=DBPASS,
                        port="5432")

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def api_call(url: str, max_retries=3) -> json:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={"X-Riot-Token" : API_KEY}, timeout=10)
            if response.status_code == 200:
                time.sleep(0.5)
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

def get_puuid(name : str, tag : str) -> str:
    response = api_call(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}")
    return response["puuid"]

def get_matches(puuid : str):
    response = api_call(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10")
    return response

def process_matches(match_list : [str], puuid : str):
    points = []
    for matchID in match_list:
        matchDataRaw = api_call(f"https://europe.api.riotgames.com/lol/match/v5/matches/{matchID}")
        for participant in matchDataRaw["info"]["participants"]:
            if participant["puuid"] != puuid:
                continue
            else:
                kills = participant["kills"]
                deaths = participant["deaths"]
                assists = participant["assists"]
                win = participant["win"]
                points.append({"x": kills, "y": deaths, "z": assists, "win": win})
                break
    return points

@app.get("/clusterManager/{name}/{tag}")

def get_player(name : str, tag : str):

    puuid = get_puuid(name, tag)
    matchList = get_matches(puuid)
    points = process_matches(matchList, puuid)

    return {
        "puuid" : puuid,
        "points" : points,
    }

@app.get("/UMAPPoints/{lane}")

def get_points(lane : str):
    cur.execute(f"SELECT * FROM player_umap_standard WHERE lane = '{lane}'")
    points = cur.fetchall()

    df = pd.DataFrame(points)

    return {
        "UMAPPoints" : points
    }
