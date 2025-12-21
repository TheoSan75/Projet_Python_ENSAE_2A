import pandas as pd
import numpy as np
from .config import RENAME_VILLES_FULL, UNAVAILABLE_VALUES, RENAME_GEODAIR


def load_and_merge_cities(path_geodair, path_villes, path_tourisme):
    """Loads raw data and performs the initial merge between Cities and Tourism."""
    data_geodair = pd.read_csv(path_geodair)
    data_villes = pd.read_csv(path_villes, sep=";")
    data_tourisme = pd.read_csv(path_tourisme, sep=";")

    data_villes.rename(columns={'Code': "CODGEO"}, inplace=True)
    df_merged = data_villes.merge(data_tourisme, on="CODGEO", how="left")
    
    return df_merged, data_geodair

def process_city_data(df):
    """Cleans city data: Renaming, NaNs, Filtering Overseas, Type casting."""
    # 1. Renaming
    df = df.rename(columns=RENAME_VILLES_FULL)

    # 2. Handle NaNs
    df = df.replace({',': '.'}, regex=True)
    df = df.replace(UNAVAILABLE_VALUES, np.nan)

    # 3. Filter specific regions (Corsica 2A/2B and Overseas 97)
    df["code_geo"] = df["code_geo"].astype(str)
    df = df[~df["code_geo"].str.startswith(("2A", "2B", "97"))]

    # 4. Type Casting
    df["libelle"] = df["libelle"].astype(str)
    numeric_cols = df.columns.drop(["code_geo", "libelle"])
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def prepare_geodair_data(df_geodair, df_villes_clean):
    """Merges Geodair data with cleaned city data."""
    # Rename
    df_geodair = df_geodair.rename(columns=RENAME_GEODAIR)

    # Standardize Merge Keys
    df_geodair['codgeo'] = df_geodair['codgeo'].astype(str).str.replace('.0', '', regex=False)

    # Prepare city data for merge (rename keys to match geodair)
    df_villes_prep = df_villes_clean.copy()
    df_villes_prep = df_villes_prep.rename(columns={'code_geo': 'codgeo', 'libelle': 'nom_commune'})
    df_villes_prep['codgeo'] = df_villes_prep['codgeo'].astype(str).str.replace('.0', '', regex=False)

    # Merge
    df_merged = pd.merge(df_geodair, df_villes_prep, on="codgeo", how="left")

    return df_merged

def aggregate_by_pollutant(df_complete):
    """Aggregates data by Pollutant and City."""
    # Define aggregation rules
    regles = {"valeur": "mean", "valeur_brute": "mean"}

    cols_first = [
        "codgeo", "nom_commune", "population_2022", "mediane_niveau_vie_2021",
        "densite_population_2022", "part_commerce_transport_services_2023",
        "part_industrie_2023", "nb_hotels_2022", "nb_etablissements_2023",
        "taux_activite_2022", "part_construction_2023", "nb_campings_2022"
    ]

    for col in cols_first:
        if col in df_complete.columns:
            regles[col] = "first"
         
    return df_complete.groupby(["polluant", "ville"], as_index=False).agg(regles)
