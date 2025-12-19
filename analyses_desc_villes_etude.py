#########################################
#####  Analyses descriptives - Théo #####
#########################################
# Ce script donne des analyses descriptives sur nos villes d'étude (celles dans lesquelles sont présentes des stations météo)
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration pour l'affichage
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
sns.set_theme(style="whitegrid")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', None)
pd.set_option("display.max_colwidth", None)


# ===========================
# 1. CHARGEMENT DES DONNÉES
# ===========================
print("="*80)
print("CHARGEMENT DES DONNÉES")
print("="*80)

geodair_2022 = pd.read_csv("data/processed_data/geodair_2022_villes_codgeo3.csv", sep=",")
data_villes = pd.read_csv("data/processed_data/data_villes_tourisme.csv", sep=",")

print('Geodair shape:', geodair_2022.shape)
print('Data Villes shape:', data_villes.shape)
# ===========================
# 1bis. SEPARATION DES DONNÉES
# ===========================
# Pour certaines villes, il y a plusieurs points de mesure et plusieurs polluants mesurés.
# Il est nécessaire d'agréger tous les points de mesure d'une ville pour n'avoir, au final,
# qu'un point de mesure synthétique par ville.
# Ici, on se contente de diviser le dataset de mesures par polluant. L'aggrégation des mesures
# au sein d'une même ville se fera par la suite, lors des analyses.

polluants = ['O3', 'PM2.5', 'PM10', 'NOX as NO2']

datasets = {}

for polluant in polluants:
    df_pollutant = geodair_2022[geodair_2022['Polluant'] == polluant].copy()
    
    # Store the result in the dictionary
    datasets[polluant] = df_pollutant
    
    print(f"Dataset **{polluant}** created with **{len(df_pollutant)}** rows.")

print("\n---")
print("Summary")
print(datasets['O3'].shape, datasets['NOX as NO2'].shape, datasets['PM10'].shape, datasets['PM2.5'].shape)

# Sauvegarde des nouveaux datasets
output_dir = "data/processed_data/BDD_par_polluant"
for polluant, df in datasets.items():
    # Nom nettoyé
    filename = polluant.replace(' ', '_').replace('.', '_').replace('/', '_')
    file_path = os.path.join(output_dir, f"geodair_2022_{filename}.csv")
    df.to_csv(file_path, index=False)

# Merge pour avoir une observation par ville, par dataset
# NB: Les villes sont identifiées par CODGEO (unique, contrairement au nom de la ville)

for polluant, df in datasets.items():
    # Identify the city column
    city_col = "CODGEO"
    duplicates = df[df.duplicated(subset=[city_col], keep=False)]
    print(f"\n=== {polluant} ===")
    if duplicates.empty:
        print("No duplicate cities.")
    else:
        print(f"{duplicates[city_col].nunique()} unique duplicated cities found.")
        #print(duplicates[[city_col]].value_counts())


# ===========================
# 2. MERGE DES DONNÉES
# ===========================
# Merge (jointure) des données de qualité de l'air de nos villes avec les données socio-éco-démo.
print("\n" + "="*80)
print("MERGE DES DONNÉES AIR ET ECO")
print("="*80)

# CODGEO contient quelques valeurs manquantes, il faut donc le nettoyer avant le merge
# (si pandas detecte des nan, il va transformer la colonne en float, ce qui n'est pas souhaitable
# pour des CODGEO)


def clean_codgeo(df, col='CODGEO'):
    df[col] = (
        df[col]
        .astype(str)                  # Convertit en texte
        .str.replace(r'\.0$', '', regex=True) # Supprime le ".0" des floats
        .str.strip()                  # Enlève les espaces éventuels
    )
    # Sécurité : si la valeur était initialement vide (NaN), on remet un vrai NaN
    df.loc[df[col].str.contains('nan', case=False), col] = np.nan
    return df

geodair_2022 = clean_codgeo(geodair_2022)
data_villes = clean_codgeo(data_villes)
# Conversion de CODGEO en string pour les deux DataFrames
geodair_2022['CODGEO'] = geodair_2022['CODGEO'].astype(str)
data_villes['CODGEO'] = data_villes['CODGEO'].astype(str)
# Jointure des données des villes et du tourisme
data_etude = pd.merge(
    geodair_2022,
    data_villes,
    on="CODGEO",
    how="left"
)

# Vérification rapide
print(f"Lignes après fusion : {len(data_etude)}")
print(data_etude.head())
print(f"\nShapes après merge:")
print(data_villes.shape, geodair_2022.shape, data_etude.shape)
# Sauvegarde simple dans le répertoire courant
data_etude.to_csv("data/processed_data/data_etude_villes_relevees.csv", index=False, sep=";")

# A ce stade, nous avons un dataset, toujours avec 1 observation par mesure. Il reste à effectuer les étapes suivantes:
# - Moyenner les mesures réalisées dans une même ville
# - Séparer les observations de chaque polluant

# Les 4 datasets que nous auront ainsi pourront être étudiés ensuite

print("Valeurs uniques dans la colonne Polluant :", data_etude["Polluant"].unique())
# Liste des colonnes numériques à traiter
numeric_cols = [
    "valeur", "valeur brute", "Part des effectifs des commerces, transports, services divers 2023",
    "Population municipale 2022", "Nombre d'établissements 2023", "Densité de population (historique depuis 1876) 2022",
    "Taux d'activité par tranche d'âge 2022", "Médiane du niveau de vie 2021", 
    "Part des effectifs de l'industrie 2023", "Part des effectifs de la construction 2023", 
    "Nb_hotels_2022", "Nb_campings_2022"
]

for col in numeric_cols:
    if col in data_etude.columns:
        # errors='coerce' remplace les textes (comme 'N/A - secret statistique') par du vide (NaN)
        # On remplace d'abord la virgule par le point si c'est du texte
        if data_etude[col].dtype == 'object':
            data_etude[col] = data_etude[col].astype(str).str.replace(',', '.', regex=False)
        
        data_etude[col] = pd.to_numeric(data_etude[col], errors='coerce')

# 2. Définition des règles d'agrégation
# On moyenne les valeurs de pollution, et on garde la 1ère valeur pour les stats de la ville
agg_rule= {"valeur": "mean", "valeur brute": "mean"}
id_cols = [
    "CODGEO", "Libellé", "Part des effectifs des commerces, transports, services divers 2023",
    "Population municipale 2022", "Nombre d'établissements 2023", "Densité de population (historique depuis 1876) 2022",
    "Taux d'activité par tranche d'âge 2022", "Médiane du niveau de vie 2021", 
    "Part des effectifs de l'industrie 2023", "Part des effectifs de la construction 2023", 
    "Nb_hotels_2022", "Nb_campings_2022"
]
for col in id_cols:
    if col in data_etude.columns:
        agg_rule[col] = "first"

# Application de l'agrégation par Polluant et par Ville
df_grouped = data_etude.groupby(["Polluant", "Ville"], as_index=False).agg(agg_rule)

# 3. Séparation des observations en 4 datasets (un par polluant)
polluants = df_grouped["Polluant"].unique()
print(polluants)
datasets = {}

for pol in polluants:
    datasets[pol] = df_grouped[df_grouped["Polluant"] == pol]
    # Sauvegarde en fichier CSV
    datasets[pol].to_csv(f"data/processed_data/BDD_par_polluant/dataset_{pol}_final.csv", index=False, sep=';')
    print(f"Fichier généré : dataset_{pol}.csv ({len(datasets[pol])} villes)")

# Enfin, petit check que nos 4 nouveaux jeux de données sont ceux que l'on souhaite:

for pol in polluants:
    # 1. récuperation du dataset spécifique
    temp_df = datasets[pol]
    
    # --- ÉTAPE DE VÉRIFICATION ---
    
    # Check 1: Un seul polluant présent
    unique_pols = temp_df["Polluant"].unique()
    if len(unique_pols) != 1 or unique_pols[0] != pol:
        raise ValueError(f"ERREUR : Le dataset pour {pol} contient des polluants inattendus : {unique_pols}")

    # Check 2: Une seule observation par ville
    # On vérifie si le nombre de lignes est égal au nombre de villes uniques
    if temp_df["Ville"].nunique() != len(temp_df):
        duplicate_cities = temp_df["Ville"][temp_df["Ville"].duplicated()].tolist()
        raise ValueError(f"ERREUR : Le dataset pour {pol} contient des doublons pour les villes suivantes : {duplicate_cities}")

    # -----------------------------

    # 2. Sauvegarde si les tests passent
    file_path = f"data/processed_data/BDD_par_polluant/dataset_{pol}_final.csv"
    temp_df.to_csv(file_path, index=False, sep=';')
    
    print(f"✅ Vérification réussie pour {pol} : {len(temp_df)} villes uniques. Fichier sauvegardé.")


# ===================================
# 3. STATISTIQUES DESCRIPTIVES VILLES / COMPARAISON AVEC LES VILLES DE FRANCE
# ===================================

def check_distribution_taille(df_sample, df_france):
    # Définition des strates de population
    bins = [0, 2000, 10000, 50000, np.inf]
    labels = ['Rurale (<2k)', 'Petite ville (2k-10k)', 'Moyenne (10k-50k)', 'Grande (>50k)']
    
    # Calcul des proportions dans la France entière
    fr_counts = pd.cut(df_france['Population municipale 2022'], bins=bins, labels=labels).value_counts(normalize=True) * 100
    
    # Calcul des proportions dans votre échantillon
    sample_counts = pd.cut(df_sample['Population municipale 2022'], bins=bins, labels=labels).value_counts(normalize=True) * 100
    
    df_comp = pd.DataFrame({'France %': fr_counts, 'Echantillon %': sample_counts}).sort_index()
    print("\n--- Comparaison des strates de population ---")
    print(df_comp.round(1))

def check_economie(df_sample, df_france):
    vars_eco = [
        "Part des effectifs de l'industrie 2023",
        "Part des effectifs des commerces, transports, services divers 2023",
        "Médiane du niveau de vie 2021"
    ]
    res = []
    for var in vars_eco:
        res.append({
            "Variable": var,
            "Médiane France": df_france[var].median(),
            "Médiane Échantillon": df_sample[var].median(),
            "Différence": df_sample[var].median() - df_france[var].median()
        })
    print("\n--- Comparaison des indicateurs économiques (Médianes) ---")
    print(pd.DataFrame(res).round(2))

for pol in polluants:
    df_sample = datasets[pol]
    check_distribution_taille(df_sample, data_villes)
    check_economie(df_sample, data_villes)

