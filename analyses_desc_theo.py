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

data_air = pd.read_csv("data/raw_data/Export Moy. annuelle - 20251120135910 - 2022-01-01 00_00 - 2022-12-31 23_00.csv")
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
# Plot and save each numeric column
numeric_cols = df_villes.columns[2:]
for col in numeric_cols:
    plt.figure(figsize=(8, 4))
    data = df_villes[col].dropna() + 1e-6  # avoid log(0)
    bins = np.logspace(np.log10(data.min()), np.log10(data.max()), 50)
    plt.hist(data, bins=bins, color='skyblue', edgecolor='black')
    plt.xscale('log')
    plt.xlabel(col)
    plt.ylabel('Count')
    plt.title(f'Distribution of {col} (log scale)')
    plt.tight_layout()
    
    # Save figure to file
    filename = f"outputs/Desc_All_Cities/hist_{col}.png".replace(" ", "_")
    plt.savefig(filename)
    plt.close()  # close to avoid blocking
    print(f"Saved histogram for {col} as {filename}")
"""
# Convertir les colonnes en numérique
cols_to_convert = data_villes_tourisme.columns[2:].tolist()
print(f"Nombre de colonnes à convertir: {len(cols_to_convert)}")

conversions_success = 0
conversions_failed = []

for col in cols_to_convert:
    try:
        # Convertir en numérique, les valeurs non-numériques deviennent NaN
        data_villes_tourisme[col] = pd.to_numeric(data_villes_tourisme[col], errors='coerce')
        conversions_success += 1
    except Exception as e:
        conversions_failed.append(col)
        print(f"Erreur lors de la conversion de '{col}': {e}")

print(f"\nConversions réussies: {conversions_success}/{len(cols_to_convert)}")
if conversions_failed:
    print(f"Conversions échouées: {len(conversions_failed)}")
    print(f"  Colonnes: {conversions_failed[:5]}{'...' if len(conversions_failed) > 5 else ''}")

# Afficher le nombre de valeurs manquantes créées
n_missing_created = data_villes_tourisme[cols_to_convert].isnull().sum().sum()
print(f"✓ Valeurs manquantes créées lors de la conversion: {n_missing_created}")"""