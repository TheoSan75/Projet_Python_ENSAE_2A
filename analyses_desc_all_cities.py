#########################################
#####  Analyses descriptives - Théo #####
#########################################
import pandas as pd
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

data_air = pd.read_csv("data/raw_data/data_air_2022.csv")
data_villes = pd.read_csv("data/raw_data/data.csv", sep=";")
data_tourisme = pd.read_csv("data/raw_data/BDD_tourisme_communes_2022.csv", sep=";")

# ===========================
# 2. MERGE DES DONNÉES
# ===========================
print("\n" + "="*80)
print("MERGE DES DONNÉES VILLES ET TOURISME")
print("="*80)

# Jointure des données des villes et du tourisme
data_villes.rename(columns={'Code': "CODGEO"}, inplace=True)
print(f"Colonnes data_villes: {list(data_villes.columns)[:5]}...")
print(f"Colonnes data_tourisme: {list(data_tourisme.columns)[:5]}...")

data_villes_tourisme = data_villes.merge(data_tourisme, on="CODGEO", how="left")
print(f"\nShapes après merge:")
print(data_villes.shape, data_tourisme.shape, data_villes_tourisme.shape)


## Sauvegarde du dataset merged
#data_villes_tourisme.to_csv("Projet_Python_ENSAE_2A/data/processed_data/data_villes_tourisme.csv", index=False)
#
#print(f"\ndata_air shape: {data_air.shape}")

# ===================================
# 3. STATISTIQUES DESCRIPTIVES VILLES
# ===================================

################## 3.1. Renommage des colonnes ##################

# Nouveau nom pour les colonnes
data_villes_tourisme = data_villes_tourisme.rename(columns={
    "CODGEO": "code_geo",
    "Libellé": "libelle",
    "Part des effectifs des commerces, transports, services divers 2023": "part_commerce_transport_services_2023",
    "Population municipale 2022": "population_2022",
    "Nombre d'établissements 2023": "nb_etablissements_2023",
    "Densité de population (historique depuis 1876) 2022": "densite_population_2022",
    "Taux d'activité par tranche d'âge 2022": "taux_activite_2022",
    "Médiane du niveau de vie 2021": "mediane_niveau_vie_2021",
    "Part des effectifs de l'industrie 2023": "part_industrie_2023",
    "Part des effectifs de la construction 2023": "part_construction_2023",
    "Nb_hotels_2022": "nb_hotels_2022",
    "Nb_campings_2022": "nb_campings_2022"
})

print(data_villes_tourisme.head())

################## 3.2. Valeurs manquantes ##################

df_villes = data_villes_tourisme.copy()

unavailable_values = [
    "N/A - résultat non disponible",
    "N/A - division par 0",
    "N/A - secret statistique"
]

# Creation d'une BDD synthétisant l'analyse
report = pd.DataFrame(index=df_villes.columns, columns=unavailable_values)
report[:] = 0  # initialisation avec des 0

# On compte les occurrences de chaque N/A
for col in df_villes.columns:
    for token in unavailable_values:
        report.loc[col, token] = (df_villes[col] == token).sum()

# Remplacement des valeurs manquantes
df_villes = df_villes.replace({',': '.'}, regex=True)
df_villes = df_villes.replace(unavailable_values, np.nan)

# Affichage du bilan
print(report)
print(df_villes.shape)

################## 3.3. Suppression des villes hors Métropole ##################

# Suppression des villes dont le code geo commence par 97, 2A, 2B (Outre-mer et Corse)
# S'assurer que code_geo est une chaîne
df_villes["code_geo"] = df_villes["code_geo"].astype(str)

# Supprimer les lignes dont le code commence par 2A, 2B ou 97
df_villes = df_villes[~df_villes["code_geo"].str.startswith(("2A", "2B", "97"))]
print(df_villes.shape)

nan_report = pd.DataFrame({
    "column": df_villes.columns,
    "num_nan": df_villes.isna().sum()
})

print(nan_report)

################## 3.4. Transformation des types ##################

# Transformer les deux premières colonnes en texte
df_villes["code_geo"] = df_villes["code_geo"].astype(str)
df_villes["libelle"] = df_villes["libelle"].astype(str)

# Transformer toutes les autres colonnes en float
for col in df_villes.columns[2:]:
    df_villes[col] = pd.to_numeric(df_villes[col], errors='coerce')

# Vérifier les types
print(df_villes.dtypes)

################## 3.5. Visualisation des distributions ##################
# Les valeurs manquantes sont supprimées car peu nombreuses et il s'agit ici uniquement d'avoir une idée des distributions.
# La colonne Mediane_niveau_vie_2021 contient elle beaucoup plus de valeurs manquantes.
## Distributions en Échelle Logarithmique (Simples)
numeric_cols = df_villes.columns[2:].drop("nb_campings_2022")
print("Numeric cols:", numeric_cols)
for col in numeric_cols:
    plt.figure(figsize=(9, 5))
    data = df_villes[col].dropna() + 1e-6
    sns.histplot(
        data,
        color=sns.color_palette("viridis")[0],
        edgecolor='black',
        alpha=0.7,
        log_scale=True,
        kde=True,
    )
    plt.xlabel(col, fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title(f'Distribution de **{col}** (Échelle Logarithmique)', fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    filename = f"output/Desc_All_Cities/hist_{col}.png".replace(" ", "_")
    plt.savefig(filename, dpi=300)
    plt.close()

## Distribution de nb_campings_2022 (Échelle Linéaire)
col = "nb_campings_2022"

plt.figure(figsize=(9, 5))
data = df_villes[col].dropna()
max_campings = int(data.max())
sns.histplot(
    data,
    color=sns.color_palette("pastel")[1],
    edgecolor='black',
    alpha=0.8,
    discrete=True,
    shrink=0.8
)
plt.xlabel(col, fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.title(f'Distribution de **{col}** (Échelle Linéaire)', fontsize=14, fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
filename = f"output/Desc_All_Cities/hist_linear_{col}.png"
plt.savefig(filename, dpi=300)
plt.close()