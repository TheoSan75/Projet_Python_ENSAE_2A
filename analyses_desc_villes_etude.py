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

# ===========================
# 0. CONFIGURATION ET MAPPING
# ===========================

# Dictionnaire pour renommer les colonnes de GEODAIR (Nom courant -> Clean Snake_case)
rename_geodair = {
    'Date de début': 'date_debut',
    'Date de fin': 'date_fin',
    'Organisme': 'organisme',
    'code zas': 'code_zas',
    'Zas': 'nom_zas',
    'code site': 'code_site',
    'nom site': 'nom_site',
    'type d\'implantation': 'type_implantation',
    'Polluant': 'polluant',
    'type d\'influence': 'type_influence',
    'Réglementaire': 'reglementaire',
    'type d\'évaluation': 'type_evaluation',
    'type de valeur': 'type_valeur',
    'valeur': 'valeur',
    'valeur brute': 'valeur_brute',
    'unité de mesure': 'unite',
    'taux de saisie': 'taux_saisie',
    'couverture temporelle': 'couverture_temporelle',
    'couverture de données': 'couverture_donnees',
    'code qualité': 'code_qualite',
    'validité': 'validite',
    'Latitude': 'latitude_site',
    'Longitude': 'longitude_site',
    'Ville': 'ville',
    'CODGEO': 'codgeo',
    'Latitude_commune': 'latitude_commune',
    'Longitude_commune': 'longitude_commune'
}

# Dictionnaire pour renommer les colonnes de DATA_VILLES
rename_villes = {
    'code_geo': 'codgeo',
    'libelle': 'nom_commune'
}

# Dictionnaire pour l'AFFICHAGE (Graphiques, Titres)
# Utilisation : graph_labels.get(ma_colonne, ma_colonne)
graph_labels = {
    # --- Données Qualité de l'Air (Geodair) ---
    'valeur': 'Concentration (moy. annuelle)',
    'polluant': 'Polluant',
    'nom_site': 'Station de mesure',
    'type_implantation': 'Type d\'implantation',
    'type_influence': 'Type d\'influence',
    'organisme': 'Organisme (AASQA)',
    'ville': 'Ville',
    'unite': 'Unité de mesure',
    'nom_zas': 'Zone Administrative (ZAS)',
    # --- Données Démographiques & Économiques (Villes) ---
    'nom_commune': 'Commune',
    'population_2022': 'Population (2022)',
    'densite_population_2022': 'Densité de population (hab/km²)',
    'mediane_niveau_vie_2021': 'Niveau de vie médian (€)',
    'taux_activite_2022': 'Taux d\'activité (%)',
    'nb_etablissements_2023': 'Nombre total d\'établissements',
    # --- Données Tourisme ---
    'nb_hotels_2022': 'Nombre d\'hôtels',
    'nb_campings_2022': 'Nombre de campings',
    # --- Parts sectorielles (%) ---
    'part_commerce_transport_services_2023': 'Part Commerce & Services (%)',
    'part_industrie_2023': 'Part Industrie (%)',
    'part_construction_2023': 'Part Construction (%)'
}
# ===========================
# 1. CHARGEMENT DES DONNÉES ET RENOMMAGE
# ===========================

# On charge les deux fichiers principaux
geodair = pd.read_csv("data/processed_data/geodair_2022_villes_codgeo2.csv", sep=",")
data_villes = pd.read_csv("data/processed_data/data_villes_tourisme.csv", sep=",")
# Renommage des colonnes
geodair = geodair.rename(columns=rename_geodair)
data_villes = data_villes.rename(columns=rename_villes)

print("Colonnes Geodair :", geodair.columns.tolist())
print("-" * 20)
print("Colonnes Villes :", data_villes.columns.tolist())
# ===========================
# 2. NETTOYAGE ET MERGE
# ===========================

# On nettoie la colonne codgeo pour être sûr que la fusion marche bien
# On transforme en texte et on enlève les '.0' qui traînent
geodair['codgeo'] = geodair['codgeo'].astype(str).str.replace('.0', '', regex=False)
data_villes['codgeo'] = data_villes['codgeo'].astype(str).str.replace('.0', '', regex=False)

# On colle les infos des villes sur les mesures de l'air
df_merged = pd.merge(geodair, data_villes, on="codgeo", how="left")

# Liste des colonnes à conserver
cols_to_keep = [
    'polluant',
    'valeur',
    'valeur_brute',
    'unite',
    'ville',
    'codgeo',
    'latitude_site',
    'longitude_site',
    'latitude_commune',
    'longitude_commune',
    'part_commerce_transport_services_2023',
    'population_2022',
    'nb_etablissements_2023',
    'densite_population_2022',
    'taux_activite_2022',
    'mediane_niveau_vie_2021',
    'part_industrie_2023',
    'part_construction_2023',
    'nb_hotels_2022',
    'nb_campings_2022'
]

# On crée un nouveau DataFrame propre avec .copy() pour éviter les problèmes
df_complet = df_merged[cols_to_keep].copy()

# Affichage de vérification
print(f"Dimensions du DataFrame final : {df_complet.shape}")
print(df_complet.head())
# Sauvegarde
df_complet.to_csv("data/processed_data/data_etude_villes_relevees.csv", index=False, sep=";")

# ===========================
# 3. NETTOYAGE DES COLONNES NUMÉRIQUES
# ===========================

# Liste des colonnes qui contiennent des chiffres (et du texte comme 'N/A')
colonnes_numeriques = ['valeur', 'valeur_brute', 'part_commerce_transport_services_2023',
                    'population_2022', 'nb_etablissements_2023', 'densite_population_2022',
                    'taux_activite_2022', 'mediane_niveau_vie_2021', 'part_industrie_2023',
                    'part_construction_2023', 'nb_hotels_2022', 'nb_campings_2022'
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
regles_agregation = {"valeur": "mean", "valeur_brute": "mean"}

# Pour toutes les autres colonnes utiles, on garde la première valeur ('first')
colonnes_a_garder = [
    "codgeo", "nom_commune", "population_2022", "mediane_niveau_vie_2021",
    "densite_population_2022",
    "part_commerce_transport_services_2023",
    "part_industrie_2023", "nb_hotels_2022", "nb_etablissements_2023", "taux_activite_2022",
    "part_construction_2023", "nb_campings_2022"
]

for col in colonnes_a_garder:
    if col in df_complet.columns:
        regles_agregation[col] = "first"

# On groupe par Polluant et par Ville
df_groupe = df_complet.groupby(["polluant", "ville"], as_index=False).agg(regles_agregation)

# ===========================
# 5. SÉPARATION, SAUVEGARDE ET ANALYSE
# ===========================

liste_polluants = df_groupe["polluant"].unique()
print(f"Polluants trouvés : {liste_polluants}")

for pol in liste_polluants:
    print(f"\n--- TRAITEMENT : {pol} ---")

    # 1. On filtre pour ne garder que ce polluant
    df_polluant = df_groupe[df_groupe["polluant"] == pol]

    # 2. Vérifications de sécurité
    # On vérifie qu'il n'y a pas de doublons de ville
    if df_polluant["ville"].duplicated().any():
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
    france_dist = pd.cut(data_villes['population_2022'], bins=bins, labels=labels).value_counts(normalize=True) * 100
    # Répartition Echantillon
    sample_dist = pd.cut(df_polluant['population_2022'], bins=bins, labels=labels).value_counts(normalize=True) * 100

    print("\n   -> Comparaison des tailles de ville (%):")
    comparison = pd.DataFrame({'France': france_dist, f'Echantillon ({pol})': sample_dist})
    print(comparison.round(1))

    # B. Comparaison Niveau de vie et Services (médianes)
    med_vie_fr = data_villes['mediane_niveau_vie_2021'].median()
    med_vie_ech = df_polluant['mediane_niveau_vie_2021'].median()

    print(f"\n   -> Niveau de vie médian : France = {med_vie_fr} € | Echantillon = {med_vie_ech} €")

print("\nTerminé !")

# ===========================
# 6. ANALYSE APPROFONDIE ET VISUALISATION
# ===========================

# Liste des variables économiques à analyser
vars_eco = ["population_2022", "mediane_niveau_vie_2021",
    "densite_population_2022",
    "part_commerce_transport_services_2023",
    "part_industrie_2023", "nb_hotels_2022", "nb_etablissements_2023", "taux_activite_2022",
    "part_construction_2023", "nb_campings_2022"
]

# Création du dossier pour les graphiques s'il n'existe pas
output_dir = "data/processed_data/plots_comparaison"
os.makedirs(output_dir, exist_ok=True)

print(f"\n=== DÉBUT DE L'ANALYSE GRAPHIQUE ===")

for pol in liste_polluants:
    print(f" >> Génération des graphes pour : {pol}")
    
    # On récupère l'échantillon pour ce polluant
    df_sample = df_groupe[df_groupe["polluant"] == pol]
    
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