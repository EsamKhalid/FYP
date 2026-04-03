import pandas as pd
import psycopg2
from pandas.core.interchange.dataframe_protocol import DataFrame
from psycopg2.extras import DictCursor, execute_values
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from PythonScripts.creds import DBPASS


class CoordinatesGenerator:
    def __init__(self):
        self.conn = psycopg2.connect(database="features_db",
                                     user="postgres",
                                     host="localhost",
                                     password=DBPASS,
                                     port="5432")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


    def process_data(self):
        self.cur.execute("SELECT * FROM player_features")
        df = pd.DataFrame(self.cur.fetchall())

        features = ['gold_7', 'gold_15', 'cs_7', 'cs_15', 'xp_7', 'xp_15', 'gpm', 'cspm', 'xpm', 'dpm']
        processed_rows = []

        for lane in df['lane'].unique():
            df_lane_subset = df[df['lane'] == lane].copy()

            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(df_lane_subset[features])


            pca = PCA(n_components=3)
            pca_results = pca.fit_transform(scaled_features)

            explained_variance = pca.explained_variance_ratio_
            total_info = explained_variance.sum()

            print(f"Lane: {lane}")
            print(f"  x explains: {explained_variance[0]:.1%}")
            print(f"  y explains: {explained_variance[1]:.1%}")
            print(f"  z explains: {explained_variance[2]:.1%}")
            print(f"  retained: {total_info:.1%}")

            loadings = pd.DataFrame(
                pca.components_.T,
                columns=['x', 'y', 'z'],
                index=features
            )

            print(f"Loadings for {lane}")
            print(loadings)

            df_lane_subset[['x', 'y', 'z']] = pca_results
            processed_rows.append(df_lane_subset[['puuid', 'match_id', 'lane', 'x', 'y', 'z']])

        final_df = pd.concat(processed_rows)
        return final_df

    def insert_coordinates(self, df : pd.DataFrame):
        query = """ INSERT INTO player_coordinates (puuid, match_id, role, x, y, z) VALUES %s ON CONFLICT DO NOTHING"""
        tuples = [tuple(x) for x in df.to_numpy()]
        execute_values(self.cur, query, tuples)
        self.conn.commit()

generator = CoordinatesGenerator()

generator.insert_coordinates(generator.process_data())