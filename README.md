# Projet Python 

*Aymeric Lelièvre et Théo Sannier, 2025*

# Table des matières
1. [Objectifs](#objectifs)
2. [Sources des données](#sources)
3. [Présentation du dépôt](#pres)

## 1. Objectifs <a name="objectifs">

L'objectif est de mettre en évidence les déterminants de la pollution de l'air dans les villes en France métropolitaine, à partir de caractéristiques démographiques et économiques des villes.

## 2. Sources des données <a name="sources">

Deux sources de données sont utilisées essentiellement:

- Données de qualité de l'air (https://www.geodair.fr/): Relevé des moyennes des concentrations en O3, NOX, PM10 et PM2.5 dans l'air par les stations de mesure en France métropolitaine en 2022.
- Données économiques et démographiques des villes (https://statistiques-locales.insee.fr/): Données annuelles sur les communes de France pour les années 2021 ou 2022 ou 2023 (les données n'étant pas toutes disponibles pour 2022, nous avons utilisé certaines données de 2021 et de 2023, en faisant l'hypothèse que les variations des données d'une année à l'autre sont négligeables.)

## 3. Présentation du dépôt <a name=pres>

Le fichier synthétisant nos analyses et constituant ainsi notre rapport final est ```main.ipynb```.
Certaines fonctions plus lourdes sont définies dans des scripts du dossier ```scripts```.
Les données initiales, telles que récupérées sur internet sont localisées dans le dossier ```data/raw_data```, et les données traitées sont sauvegardées dans ```data/processed_data```.
Tous les graphiques générés (notamment les corrélogrammes et les histogrammes) sont sauvegardés et consultables dans le dossier ```output```.