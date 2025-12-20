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

# On charge les deux fichiers principaux
geodair = pd.read_csv("data/processed_data/geodair_2022_villes_codgeo3.csv", sep=",")
data_villes = pd.read_csv("data/processed_data/data_villes_tourisme.csv", sep=",")

# ===========================
# 2. NETTOYAGE ET MERGE
# ===========================

# On nettoie la colonne CODGEO pour être sûr que la fusion marche bien
# On transforme en texte et on enlève les '.0' qui traînent
geodair['CODGEO'] = geodair['CODGEO'].astype(str).str.replace('.0', '', regex=False)
data_villes['CODGEO'] = data_villes['CODGEO'].astype(str).str.replace('.0', '', regex=False)

# On colle les infos des villes sur les mesures de l'air
df_complet = pd.merge(geodair, data_villes, on="CODGEO", how="left")

# Sauvegarde
df_complet.to_csv("data/processed_data/data_etude_villes_relevees.csv", index=False, sep=";")

# ===========================
# 3. NETTOYAGE DES COLONNES NUMÉRIQUES
# ===========================

# Liste des colonnes qui contiennent des chiffres (et du texte comme 'N/A')
colonnes_numeriques = [
    "valeur", "valeur brute", "Population municipale 2022", 
    "Médiane du niveau de vie 2021", "Densité de population (historique depuis 1876) 2022",
    "Part des effectifs des commerces, transports, services divers 2023",
    "Part des effectifs de l'industrie 2023", "Nombre d'établissements 2023",
    "Nb_hotels_2022", "Nb_campings_2022"
]

# Petite fonction pour nettoyer n'importe quel dataset (notamment pour df_complet ET data_villes)
def nettoyer_chiffres(df, colonnes):
    for col in colonnes:
        if col in df.columns:
            # Si c'est du texte, on remplace la virgule par un point
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '.')
            # On force la conversion en nombre. Les erreurs deviennent NaN (vide)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# IMPORTANT : On nettoie les deux datasets !
# Sinon l'analyse comparative plantera à cause du "Secret Statistique" dans data_villes
df_complet = nettoyer_chiffres(df_complet, colonnes_numeriques)
data_villes = nettoyer_chiffres(data_villes, colonnes_numeriques)

# ===========================
# 4. AGRÉGATION (MOYENNE PAR VILLE)
# ===========================

# Dictionnaire pour dire comment on regroupe : 
# - Moyenne pour la pollution
# - On garde la première valeur trouvée pour les infos de la ville (c'est la même partout pour une ville donnée)
regles_agregation = {"valeur": "mean", "valeur brute": "mean"}

# Pour toutes les autres colonnes utiles, on garde la première valeur ('first')
colonnes_a_garder = [
    "CODGEO", "Libellé", "Population municipale 2022", "Médiane du niveau de vie 2021",
    "Densité de population (historique depuis 1876) 2022",
    "Part des effectifs des commerces, transports, services divers 2023",
    "Part des effectifs de l'industrie 2023", "Nb_hotels_2022"
]

for col in colonnes_a_garder:
    if col in df_complet.columns:
        regles_agregation[col] = "first"

# On groupe par Polluant et par Ville
df_groupe = df_complet.groupby(["Polluant", "Ville"], as_index=False).agg(regles_agregation)

# ===========================
# 5. SÉPARATION, SAUVEGARDE ET ANALYSE
# ===========================

liste_polluants = df_groupe["Polluant"].unique()
print(f"Polluants trouvés : {liste_polluants}")

for pol in liste_polluants:
    print(f"\n--- TRAITEMENT : {pol} ---")

    # 1. On filtre pour ne garder que ce polluant
    df_polluant = df_groupe[df_groupe["Polluant"] == pol]

    # 2. Vérifications de sécurité
    # On vérifie qu'il n'y a pas de doublons de ville
    if df_polluant["Ville"].duplicated().any():
        print(f"ATTENTION : Il reste des villes en double pour {pol} !")
    else:
        print(f"Check OK : Une seule ligne par ville.")

    # 3. Sauvegarde
    filename = f"data/processed_data/BDD_par_polluant/dataset_{pol}_final.csv"
    df_polluant.to_csv(filename, index=False, sep=';')

    # 4. Analyse de représentativité (Comparaison avec data_villes)

    # A. Comparaison des tailles de ville
    bins = [0, 2000, 10000, 50000, np.inf]
    labels = ['Rurale (<2k)', 'Petite (2k-10k)', 'Moyenne (10k-50k)', 'Grande (>50k)']

    # Répartition France
    france_dist = pd.cut(data_villes['Population municipale 2022'], bins=bins, labels=labels).value_counts(normalize=True) * 100
    # Répartition Echantillon
    sample_dist = pd.cut(df_polluant['Population municipale 2022'], bins=bins, labels=labels).value_counts(normalize=True) * 100

    print("\n   -> Comparaison des tailles de ville (%):")
    comparison = pd.DataFrame({'France': france_dist, f'Echantillon ({pol})': sample_dist})
    print(comparison.round(1))

    # B. Comparaison Niveau de vie et Services (médianes)
    med_vie_fr = data_villes['Médiane du niveau de vie 2021'].median()
    med_vie_ech = df_polluant['Médiane du niveau de vie 2021'].median()

    print(f"\n   -> Niveau de vie médian : France = {med_vie_fr} € | Echantillon = {med_vie_ech} €")

print("\nTerminé !")

# ===========================
# 6. ANALYSE APPROFONDIE ET VISUALISATION
# ===========================

# Liste des variables économiques à analyser
vars_eco = [
    "Population municipale 2022", 
    "Médiane du niveau de vie 2021", 
    "Densité de population (historique depuis 1876) 2022",
    "Part des effectifs des commerces, transports, services divers 2023",
    "Part des effectifs de l'industrie 2023", 
    "Nb_hotels_2022"
]

# Création du dossier pour les graphiques s'il n'existe pas
output_dir = "data/processed_data/plots_comparaison"
os.makedirs(output_dir, exist_ok=True)

print(f"\n=== DÉBUT DE L'ANALYSE GRAPHIQUE ===")

for pol in liste_polluants:
    print(f" >> Génération des graphes pour : {pol}")
    
    # On récupère l'échantillon pour ce polluant
    df_sample = df_groupe[df_groupe["Polluant"] == pol]
    
    for var in vars_eco:
        # Vérification si la colonne existe
        if var not in data_villes.columns or var not in df_sample.columns:
            continue
            
        # Nettoyage des NaNs pour le plot pour éviter les erreurs
        data_france_clean = data_villes[var].dropna()
        data_sample_clean = df_sample[var].dropna()
        
        # Calcul des moyennes
        mean_france = data_france_clean.mean()
        mean_sample = data_sample_clean.mean()
        
        # Configuration de la figure
        plt.figure(figsize=(10, 6))
        
        # Astuce : Pour la population et la densité, on passe souvent en échelle log
        # car les écarts sont trop grands (Paris vs petit village)
        log_scale = False
        if "Population" in var or "Densité" in var:
            log_scale = True
            
        # 1. Distribution France (Toile de fond)
        sns.histplot(data_france_clean, stat="density", kde=True, 
                     color="lightgray", label="France entière", 
                     log_scale=log_scale, alpha=0.5, line_kws={'lw': 1})
        
        # 2. Distribution Échantillon (Mise en avant)
        sns.histplot(data_sample_clean, stat="density", kde=True, 
                     color="teal", label=f"Échantillon ({pol})", 
                     log_scale=log_scale, alpha=0.6)
        
        # 3. Ajout des lignes de moyenne (Verticales)
        # Attention : si log_scale est actif, la moyenne arithmétique peut sembler décalée visuellement
        plt.axvline(mean_france, color='gray', linestyle='--', linewidth=2, label=f"Moyenne France : {mean_france:.1f}")
        plt.axvline(mean_sample, color='teal', linestyle='-', linewidth=2, label=f"Moyenne Éch. : {mean_sample:.1f}")
        
        # Titres et légendes
        plt.title(f"Distribution : {var}\n(Comparaison France vs Stations {pol})", fontsize=14)
        plt.legend()
        plt.xlabel(var)
        plt.ylabel("Densité")
        
        # Sauvegarde
        # On nettoie le nom du fichier (enlève les espaces/accents pour éviter les soucis)
        safe_var_name = var.replace(" ", "_").replace("'", "").replace("é", "e").replace("à", "a")[:30]
        filename_plot = f"{output_dir}/Distr_{pol}_{safe_var_name}.png"
        plt.savefig(filename_plot, bbox_inches='tight')
        plt.close() # Important pour libérer la mémoire

print(f"\nAnalyse terminée ! Les graphiques sont dans : {output_dir}")