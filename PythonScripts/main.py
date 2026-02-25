from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/player/{riot_id}")
def get_player(riot_id: str):
    return {
        "x": random.uniform(-5, 5),
        "y": random.uniform(-5, 5),
        "z": random.uniform(-5, 5),
        "cluster": random.randint(0, 2)
    }