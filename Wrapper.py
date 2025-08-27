from DB_Connect import DB_Connection
from API_Access import ApiAccess

seed_account ="aSstdTtqhoNflYWFsjsvT1Zg_u0-mJltk_qJ3v80YXazwUlsakbuNzZ8Dsb62jARsH2fbn6rM2q6Ug"

db = DB_Connection()

api = ApiAccess(db,seed_account)
api.get_player_matches()

players = ["Gold II", "Platinum IV", "Platinum III", "Gold I",
           "Gold IV", "Silver I", "Platinum II", "Gold III",
           "Platinum I", "Gold II"]

#api.get_average_rank(players)

db.close_connection()