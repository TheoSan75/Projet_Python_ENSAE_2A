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


# Conversion de CODGEO en string pour les deux DataFrames
geodair_2022['CODGEO'] = geodair_2022['CODGEO'].astype(str)
data_villes['CODGEO'] = data_villes['CODGEO'].astype(str)
# Jointure des données des villes et du tourisme
data_etude = geodair_2022.merge(data_villes, on="CODGEO", how="left")
print(f"\nShapes après merge:")
print(data_villes.shape, geodair_2022.shape, data_etude.shape)

# Sauvegarde simple dans le répertoire courant
data_etude.to_csv("data/processed_data/data_etude_villes_relevees.csv", index=False, sep=";")


# ===================================
# 3. STATISTIQUES DESCRIPTIVES VILLES
# ===================================

# On commence par construire le dataset contenant les informations socio-démo-éco de chaque ville présente
# dans chaque dataset de polluant.

cities_by_pollutant = {}

for polluant, df in datasets.items():
    unique_cities = df["CODGEO"].unique()
    print(f"\n=== {polluant} ===")
    print(f"Found {len(unique_cities)} unique cities.")
    extracted_rows = data_villes[data_villes["CODGEO"].isin(unique_cities)]
    print(f"Extracted {len(extracted_rows)} rows from data_villes.")
    cities_by_pollutant[polluant] = extracted_rows
data_villes_O3 = cities_by_pollutant['O3']
data_villes_NOX = cities_by_pollutant['NOX as NO2']
data_villes_PM10 = cities_by_pollutant['PM10']
data_villes_PM25 = cities_by_pollutant['PM2.5']

print(data_villes_O3.shape, data_villes_NOX.shape, data_villes_PM10.shape, data_villes_PM25.shape)