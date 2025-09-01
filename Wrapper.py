from DB_Connect import DBConnection
from API_Access import ApiAccess

seed_account ="cMvR1ydfnEduKBCHJ7SOA_KLlPBcsIZ7jZMH8mv8AeHbvB9-wSfO-xHXjvTdxWr9EBfxmFHRXj2HLA"

db = DBConnection()

api = ApiAccess(db,seed_account)
api.get_player_matches(seed_account)

#api.get_matches_composition()

db.close_connection()