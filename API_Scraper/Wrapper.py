from DB_Connect import DBConnection
from API_Access import ApiAccess



db = DBConnection()

api = ApiAccess(db)

#PLEASE GET RID OF DUPLICATES IN PARTICIPANTS TABLE

#api.insert_match_data()

api.complete_incomplete_matches()
api.get_rank_composition()
rank_needed = api.calculate_needed_rank()
next_seed = db.get_seed(rank_needed)["puuid"]
api.get_player_matches(next_seed)


# api.populate_timeline()

# api.ins()

#api.get_player_matches(seed_account)


#api.get_matches_composition()

#api.rerank_matches()
#api.complete_incomplete_matches()
db.close_connection()