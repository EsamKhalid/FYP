from DB_Connect import DBConnection
from API_Access import ApiAccess



db = DBConnection()

api = ApiAccess(db)

api.get_rank_composition()
api.complete_incomplete_matches()
rank_needed = api.calculate_needed_rank()
next_seed = db.get_seed(rank_needed)["puuid"]
api.get_player_matches(next_seed)

#api.get_player_matches(seed_account)


#api.get_matches_composition()

#api.rerank_matches()
#api.complete_incomplete_matches()
db.close_connection()