from fastapi import FastAPI
import random
import requests
from creds import API_KEY


app = FastAPI()

def get_puuid(name : str, tag : str) -> str:
    response = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}")
    return response.json()["puuid"]

@app.get("/clusterManager/{name}/{tag}")

def get_player(name : str, tag : str):
    return {
        "x": random.uniform(-5, 5),
        "y": random.uniform(-5, 5),
        "z": random.uniform(-5, 5),
        "cluster": random.randint(0, 2),
        "puuid" : get_puuid(name,tag),
    }
