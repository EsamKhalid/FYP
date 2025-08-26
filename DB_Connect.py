from datetime import datetime, timezone
import psycopg2
import json
import os

import API_Access

match_folder = r"C:\Api_Data\match_data"

seed_account ="aSstdTtqhoNflYWFsjsvT1Zg_u0-mJltk_qJ3v80YXazwUlsakbuNzZ8Dsb62jARsH2fbn6rM2q6Ug"

api = API_Access.ApiAccess(seed_account)

print(api.get_player_matches())