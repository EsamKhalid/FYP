Data Mining and Playstyle Clustering of League of Legends Data

A final-year project by **Esam Khalid**, Aston University (2025).

This system collects ranked match and timeline data from the Riot Games API, engineers behavioural feature vectors for each player-match pair, applies dimensionality reduction and density-based clustering to produce a three-dimensional behavioural space, and visualises the results interactively in a Unity application. Players can enter their own Riot ID to be projected into the space and locate their playstyle relative to the wider player population.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup](#setup)
  - [1. Database](#1-database)
  - [2. Python Environment](#2-python-environment)
  - [3. Credentials](#3-credentials)
  - [4. Riot API Key](#4-riot-api-key)
- [Running the FastAPI Backend](#running-the-fastapi-backend)
- [Running the Unity Frontend](#running-the-unity-frontend)
- [API Endpoints](#api-endpoints)
- [Features](#features)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The system is split into two pipelines.

**Offline pipeline** : run once to build the behavioural space from a large collected dataset.

```
Raw JSON files (match + timeline)
        │
        ▼
TimelineProcessor.process_timelines()   ← Feature extraction
        │
        ▼
TimelineProcessor.standardise()         ← Per-lane StandardScaler (saved to .sav)
        │
        ▼
TimelineProcessor.apply_umap()          ← UMAP 3D embedding (saved to .sav)
        │
        ▼
TimelineProcessor.apply_hdbscan()       ← HDBSCAN cluster labels (saved to .sav)
        │
        ▼
PostgreSQL  →  player_umap_final table  ← Served to Unity
```

**Online pipeline** : runs at request time when a player submits their Riot ID in the Unity app.

```
Unity (InputScreen)
        │  Riot ID + lane
        ▼
FastAPI  /getPlayer/{name}/{tag}/{lane}
        │
        ├── Riot Games API  (PUUID, matches, timeline, rank)
        │
        ├── Feature extraction  (same logic as offline)
        │
        ├── Pre-fitted scaler  →  standardise
        ├── Pre-fitted UMAP    →  project into existing space
        ├── Pre-fitted HDBSCAN →  hdbscan.approximate_predict()
        │
        ▼
PostgreSQL  →  player_umap_standard     ← Player points returned to Unity
        │
        ▼
Unity (Main scene)  ←  3D scatter plot rendered
```

> **NOTE: Since the offline pipeline serves to create the data points, It does not need to be run for the project to work, instead the SQL insert files containing the required data and table structures can be found at: https://www.kaggle.com/datasets/esamkhalid/fyp-dataset**

---

## Prerequisites

### Python

| Package        | Version tested | Purpose                       |
| -------------- | -------------- | ----------------------------- |
| `fastapi`      | 0.111          | Backend web framework         |
| `uvicorn`      | 0.29           | ASGI server                   |
| `requests`     | 2.31           | Riot API calls                |
| `psycopg2`     | 2.9            | PostgreSQL driver             |
| `pandas`       | 2.2            | Dataframe manipulation        |
| `scikit-learn` | 1.4            | Scaler, PCA, FA, KMeans       |
| `umap-learn`   | 0.5            | UMAP dimensionality reduction |
| `hdbscan`      | 0.8            | Density-based clustering      |
| `joblib`       | 1.4            | Model serialisation           |
| `matplotlib`   | 3.8            | Evaluation plots              |
| `seaborn`      | 0.13           | Correlation matrix heatmaps   |
| `statsmodels`  | 0.14           | Variance Inflation Factor     |
| `numpy`        | 1.26           | Numerical operations          |

### Database

- **PostgreSQL 15+** running locally on port 5432
- Database name: `features_db`

### Unity

- **Unity 6000.3.9f1** (Unity 6)
- **Newtonsoft.Json for Unity** — install via Package Manager (`com.unity.nuget.newtonsoft-json`)
- **TextMeshPro** — included with Unity

---

## Project Structure

```
playstyle-sys/
│
├── Backend/
│   ├── main.py                  # FastAPI application (online pipeline + endpoints)
│   ├── timeline_processor.py    # Offline pipeline (feature extraction, Dimensionality Reduction, clustering)
│   └── creds.py                 # API key and DB password
│
├── Models/                      # Serialised model files
│   ├── Final/
│   ├── scaler_JUNGLE.sav
│   ├── scaler_MIDDLE.sav
│   ├── scaler_BOTTOM.sav
│   ├── scaler_UTILITY.sav
│   ├── player_umap_final_TOP.sav
│   ├── player_umap_final_JUNGLE.sav
│   ├── player_umap_final_MIDDLE.sav
│   ├── player_umap_final_BOTTOM.sav
│   ├── player_umap_final_UTILITY.sav
│   ├── hdbscan_final_TOP.sav
│   ├── hdbscan_final_JUNGLE.sav
│   ├── hdbscan_final_MIDDLE.sav
│   ├── hdbscan_final_BOTTOM.sav
│   └── hdbscan_final_UTILITY.sav
│
├── Unity/
│   ├── Assets/
│   │   ├── Scripts/
│   │   │   ├── APIHandler.cs          # HTTP client
│   │   │   ├── PointSpawner.cs        # 3D point rendering + controls
│   │   │   ├── UIController.cs        # Visualisation scene UI wiring
│   │   │   ├── MainMenuController.cs  # Main menu wiring
│   │   │   └── InputScreenController.cs  # Input screen wiring
│   │   └── UI/
│   │       ├── MainMenu.uxml
│   │       ├── InputScreen.uxml
│   │       ├── VisualisationPanel.uxml
│   │       └── CyberpunkShared.uss
│   └── ...
│
├── data/                        # Offline CSVs (participants, player_ranks)
│   ├── participants.csv
│   └── player_ranks.csv
│
└── figures/                     # Evaluation plots
    ├── correlation_matrices/
    └── VIF Plots/
```

---

## Setup

### 1. Database

To set up the database, go to https://www.kaggle.com/datasets/esamkhalid/fyp-dataset and download the SQL inserts to import into the PostgreSQL database to create the tables and import the data.

### 2. Python Environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install fastapi uvicorn requests psycopg2-binary pandas \
            scikit-learn umap-learn hdbscan joblib \
            matplotlib seaborn statsmodels numpy
```

> **Note: A python venv was used during the development of this project, however it is not necessary and can be ran using a standard python environment given that all dependencies are installed**

### 3. Credentials

Create `Backend/creds.py` — **do not commit this file**:

```python
API_KEY = "RGAPI-your-riot-api-key-here"
DBPASS  = "your-postgres-password"
```

Add `creds.py` to `.gitignore`:

```
creds.py
*.sav
```

### 4. Riot API Key

Obtain a development API key from the [Riot Developer Portal](https://developer.riotgames.com). Note that development keys expire after 24 hours. The `api_call` function handles rate limiting automatically by reading the `Retry-After` header.

---

## Running the FastAPI Backend

```bash
cd PythonScripts
uvicorn main:app --host 127.0.0.1 --port 8000
```

The server must be running before launching the Unity application. To confirm it is working, open `http://127.0.0.1:8000/docs` in a browser,

> **Note:** Processing a new player for the first time can take a bit longer depending on API rate limits, as the server fetches and processes up to 20 timeline files. Subsequent requests for the same player return cached database results immediately.

---

## Running the Unity Frontend

1. Go to the Builds folder and run FYP.exe
2. Ensure the FastAPI backend is running on `http://127.0.0.1:8000`.
3. Navigate to the input screen, enter a Riot ID in the format `Name#Tag`, select the lane the player plays, and submit.
4. The application will transition to the Main scene once processing completes and render the 3D cluster space with the player's matches highlighted.

---

## API Endpoints

### `GET /getPlayer/{name}/{tag}/{lane}`

Processes a player's recent ranked matches for the specified lane and returns their three-dimensional embeddings alongside the full cluster dataset.

**Path parameters:**

| Parameter | Description             | Example     |
| --------- | ----------------------- | ----------- |
| `name`    | Riot ID game name       | `SpilltTea` |
| `tag`     | Riot ID tag line        | `TEA`       |
| `lane`    | Lane (case-insensitive) | `MIDDLE`    |

**Success response:**

```json
{
  "playerPoints": [ { "puuid": "...", "match_id": "...", "lane": "MIDDLE", "win": true, "x": 1.2, "y": -0.4, "z": 0.9, "cluster": 2, "current_rank": "GOLD" } ],
  "points": [ ... ],
  "success": true,
  "error": "None",
}
```

**Error response:**

```json
{
  "playerPoints": null,
  "points": null,
  "success": false,
  "error": "Not currently ranked"
}
```

---

## Features

The following 25 features are engineered per player-match pair. Features at minutes 7 and 15 are extracted from the timeline file; all other features come from the match summary.

| Feature                  | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| `gold_7`, `gold_15`      | Total gold at minutes 7 and 15                                   |
| `cs_7`, `cs_15`          | Creep score (minions + jungle camps) at minutes 7 and 15         |
| `xp_7`, `xp_15`          | Experience at minutes 7 and 15                                   |
| `damage_7`, `damage_15`  | Damage dealt to champions at minutes 7 and 15                    |
| `roaming_15`             | Cumulative Euclidean distance moved in the first 15 minutes      |
| `gpm`                    | Gold per minute (full match)                                     |
| `cspm`                   | Creep score per minute (full match)                              |
| `xpm`                    | Experience per minute (full match)                               |
| `dpm`                    | Damage per minute (full match)                                   |
| `total_gold`             | Total gold earned                                                |
| `total_cs`               | Total creep score                                                |
| `total_xp`               | Total experience                                                 |
| `total_damage`           | Total damage dealt to champions                                  |
| `total_damage_taken`     | Total damage received                                            |
| `total_roaming_distance` | Total Euclidean distance moved across the full match             |
| `kda`                    | (Kills + Assists) / max(Deaths, 1)                               |
| `kill_participation`     | Player kills / total team kills                                  |
| `cc_score`               | Total time enemies spent in crowd control applied by this player |
| `vision_score`           | Vision score (wards placed, cleared, vision bought)              |
| `turret_damage`          | Damage dealt to turrets                                          |
| `objective_damage`       | Damage dealt to objectives (Baron, Dragon, Herald)               |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'creds'`**
Create `Backend/creds.py` with your `API_KEY` and `DBPASS` as shown in [Setup](#3-credentials).

**`psycopg2.OperationalError: could not connect to server`**
Ensure PostgreSQL is running and the credentials in `creds.py` are correct. The default port is 5432.

**`FileNotFoundError: ../Models/Final/<filename>.sav`**
You might be missing one of the serialised models, which might be due to the github file size limit when commiting the .sav files. In this case, go to https://www.kaggle.com/datasets/esamkhalid/fyp-dataset and download the sav files.

**Unity shows a connection error on scan**
Confirm the FastAPI server is running on `http://127.0.0.1:8000`. Check for firewall rules blocking localhost connections.

**Player scan takes a long time**
This is expected on first scan since the backend fetches and processes up to 20 timeline files from the Riot API. The server request timeout in `APIHandler.cs` is set to 90 seconds. Subsequent scans for the same player return cached data immediately.
