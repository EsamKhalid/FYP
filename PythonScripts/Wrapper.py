from DB_Connect import DBConnection
from API_Access import ApiAccess

db = DBConnection()

api = ApiAccess(db)

# Initiate scraping algorithm
# rank_needed = api.calculate_needed_rank()
# next_seed = db.get_seed(rank_needed)["puuid"]
# rank = db.get_player_rank(next_seed)
# api.get_player_matches(next_seed, rank["current_rank"], rank["current_division"])

api.get_rank_composition()

db.close_connection()