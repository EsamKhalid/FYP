from creds import API_Key
import requests

player_list = r"C:/Api_Data/PlayerList.txt"
last_scraped_player = r"C:/Api_Data/Last_Scraped.txt"

headers = {"X-Riot-Token": API_Key}



challenger_list = requests.get("https://br1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5", headers=headers).json()


for entry in challenger_list["entries"]:
    print(entry["puuid"])

