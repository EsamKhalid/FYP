from DB_Connect import DBConnection
from API_Access import ApiAccess

seed_account ="JEn7PKtqhGXOI6asbNskDIeoNhYusnNacQZ3IQR9W8RgNnjx5lfew6C2OoRzB7Aunjq9yuamiscoBQ"

db = DBConnection()

api = ApiAccess(db,seed_account)
#api.get_player_matches(seed_account)

#api.update_player_ranks()

api.get_matches_composition()

db.close_connection()