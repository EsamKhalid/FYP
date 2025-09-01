from DB_Connect import DBConnection
from API_Access import ApiAccess

seed_account ="aSstdTtqhoNflYWFsjsvT1Zg_u0-mJltk_qJ3v80YXazwUlsakbuNzZ8Dsb62jARsH2fbn6rM2q6Ug"

db = DBConnection()

api = ApiAccess(db,seed_account)
api.get_player_matches(seed_account)

#api.update_player_ranks()


db.close_connection()