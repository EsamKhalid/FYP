import json
from http.client import responses

from fastapi import FastAPI
import random
import requests
from creds import API_KEY
import time


app = FastAPI()


def api_call(url: str, max_retries=3) -> json:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={"X-Riot-Token" : API_KEY}, timeout=10)

            if response.status_code == 200:
                time.sleep(0.35)
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

@app.get("/clusterManager/{name}/{tag}")

def get_player(name : str, tag : str):

    puuid = get_puuid(name, tag)
    matchList = get_matches(puuid)
    points = []
    for matchID in matchList:
        matchDataRaw = api_call(f"https://europe.api.riotgames.com/lol/match/v5/matches/{matchID}")
        for participant in matchDataRaw["info"]["participants"]:
            if participant["puuid"] != puuid:
                continue
            else:
                kills = participant["kills"]
                deaths = participant["deaths"]
                assists = participant["assists"]
                win = participant["win"]
                points.append({"x" : kills, "y" : deaths, "z" : assists, "win" : win})
                break

    return {
        "x": random.uniform(-5, 5),
        "y": random.uniform(-5, 5),
        "z": random.uniform(-5, 5),
        "cluster": random.randint(0, 2),
        "puuid" : puuid,
        "points" : points,
    }

