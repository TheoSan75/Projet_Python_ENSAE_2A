import pandas as pd
import numpy as np
from scripts.config import RENAME_VILLES_FULL, UNAVAILABLE_VALUES, RENAME_GEODAIR


def load_and_merge_cities(path_geodair, path_villes, path_tourisme):
    """Import des données et jointure des données touristiques sur les villes"""
    data_geodair = pd.read_csv(path_geodair)
    data_villes = pd.read_csv(path_villes, sep=";")
    data_tourisme = pd.read_csv(path_tourisme, sep=";")

    data_villes.rename(columns={'Code': "CODGEO"}, inplace=True)
    df_merged = data_villes.merge(data_tourisme, on="CODGEO", how="left")

    return df_merged, data_geodair


def process_city_data(df):
    """Nettoyage du dataframe des villes"""
    # Renommage
    df = df.rename(columns=RENAME_VILLES_FULL)

    # Gestion des valeurs manquantes
    df = df.replace({',': '.'}, regex=True)
    df = df.replace(UNAVAILABLE_VALUES, np.nan)

    # Suppressions des villes de Corse et d'outre-mer
    df["code_geo"] = df["code_geo"].astype(str)
    df = df[~df["code_geo"].str.startswith(("2A", "2B", "97"))]

    # Gestion des types
    df["libelle"] = df["libelle"].astype(str)
    numeric_cols = df.columns.drop(["code_geo", "libelle"])
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def prepare_geodair_data(df_geodair, df_villes_clean):
    """Fusion des données météo avec le dataset des villes"""
    # Renommage
    df_geodair = df_geodair.rename(columns=RENAME_GEODAIR)

    # Nettoyage de valeur et valeur_brute
    cols_pollution = ['valeur', 'valeur_brute']
    for col in cols_pollution:
        if col in df_geodair.columns:
            # Si c'est du string, on remplace virgule par point
            if df_geodair[col].dtype == 'object':
                df_geodair[col] = df_geodair[col].str.replace(',', '.')
            df_geodair[col] = pd.to_numeric(df_geodair[col], errors='coerce')

    # Standardisation de la colonne de jointure (pour éviter son dédoublement)
    df_geodair['codgeo'] = df_geodair['codgeo'].astype(str).str.replace('.0', '', regex=False)

    # Renommage des colonnes avant la jointure
    df_villes_prep = df_villes_clean.copy()
    df_villes_prep = df_villes_prep.rename(columns={'code_geo': 'codgeo', 'libelle': 'nom_commune'})
    df_villes_prep['codgeo'] = df_villes_prep['codgeo'].astype(str).str.replace('.0', '', regex=False)

    # Jointure
    df_merged = pd.merge(df_geodair, df_villes_prep, on="codgeo", how="left")

    return df_merged


def aggregate_by_pollutant(df_complete):
    """Aggrégation des mesures de l'air par polluant et par ville"""
    # Définition des règles d'aggrégation
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
    df_aggrege = df_complete.groupby(["polluant", "ville"], as_index=False).agg(regles)
    df_aggrege = df_aggrege.drop("nom_commune", axis=1)
    return df_aggrege


def analyze_city_size_distribution(df, pol_name):
    """
    Calcule la concentration moyenne de chaque polluant dans chaque taille de ville
    """
    # Duplication du dataframe pour éviter son altération
    df_calc = df.copy()

    # Définition de 4 catégories de villes, selon leur population
    # Rurale (<2k), Petite (2-10k), Moyenne (10-50k), Grande (>50k)
    bins = [0, 2000, 10000, 50000, float('inf')]
    labels = ['Rurale (<2k)', 'Petite (2-10k)', 'Moyenne (10-50k)', 'Grande (>50k)']

    # Vérification qu'une colonne population_2022 existe bien
    if 'population_2022' not in df_calc.columns:
        print("Erreur: Colonne 'population_2022' manquante.")
        return

    # Création de la colonne contenant la catégorie de la ville
    # right=False pour que la borne à gauche soit incluse: [0, 2000), [2000, 10000), etc.
    df_calc['taille_ville'] = pd.cut(df_calc['population_2022'], bins=bins, labels=labels, right=False)

    # Calcul des statistiques
    # observed=False assure que toutes les catégories sont affichées, même si elles ont pour valeur 0
    stats = df_calc.groupby('taille_ville', observed=False).agg(
        Nb_Villes=('valeur', 'count'),
        Moyenne_Mesures=('valeur', 'mean')
    )

    # Calcul des proportions de chaque ville
    total_villes = len(df_calc)
    if total_villes > 0:
        stats['Proportion (%)'] = (stats['Nb_Villes'] / total_villes * 100).round(2)
    else:
        stats['Proportion (%)'] = 0.0

    # Arrondi des moyennes pour un affichage plus propre
    stats['Moyenne_Mesures'] = stats['Moyenne_Mesures'].round(3)

    # Nouvel ordre des colonnes
    stats = stats[['Nb_Villes', 'Proportion (%)', 'Moyenne_Mesures']]

    # Affichage
    print(f"\n>> Distribution par taille de ville pour : {pol_name}")
    return stats
