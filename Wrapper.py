from DB_Connect import DBConnection
from API_Access import ApiAccess

seed_account ="ZRLynfMwNWzPsiLGbcatwOXsGNm4DpoUEbWrBn5UeLztw-SLxFufx_HDGoM2uKQ4lR2uO16u1OJzeQ"

db = DBConnection()

api = ApiAccess(db)
#api.get_player_matches(seed_account)

print(api.get_player_rank("ZRLynfMwNWzPsiLGbcatwOXsGNm4DpoUEbWrBn5UeLztw-SLxFufx_HDGoM2uKQ4lR2uO16u1OJzeQ"))

#NEED TO CLEAN UP DATABASE, ACCIDENTALLY INCLUDED RANKED FLEX. LOOP THROUGH EVERY PLAYER AND RECALCULATE THEIR RANK

#api.get_matches_composition()


#api.complete_incomplete_matches()
db.close_connection()