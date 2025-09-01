from DB_Connect import DBConnection
from API_Access import ApiAccess

seed_account ="vm9YlQmcZMOPx34z8Q2SV7iU-X8meP46ponqNt-J0v3DceMoIzZEZEvPKGx19G9fbyAqU5ontRSJvQ"

db = DBConnection()

api = ApiAccess(db)
#api.get_player_matches(seed_account)

#api.get_matches_composition()

print(db.get_seed(api.get_matches_composition()))

#api.complete_incomplete_matches()
db.close_connection()