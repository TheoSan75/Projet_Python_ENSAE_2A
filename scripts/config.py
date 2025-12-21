# Dictionnaire pour renommer les colonnes de la BDD des villes de France
RENAME_VILLES_FULL = {
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
}

# Dictionnaire pour renommer les colonnes de la BDD Geodair
RENAME_GEODAIR = {
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

# Valeurs à traiter en NaNs
UNAVAILABLE_VALUES = [
    "N/A - résultat non disponible",
    "N/A - division par 0",
    "N/A - secret statistique"
]