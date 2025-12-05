# Méthodologie envisagée

- Construire la BDD des villes par jointure sur une seule année - Théo

### Analyses descriptives des villes ayant un point de mesure

- Démographie (nbre d'habitants, densité de pop, proportion de pop active/chomage, niveau de vie)
- Activité économique par secteur (Nombre d'entreprises, de commerces, tourisme etc.)
- PIB régional (et autres indicateurs aggrégés ?)
- Quelques analyses sur les polluants (valeur moyenne, relations entre eux)

Viz:
- Carte des communes/stations dans la liste - Aymeric
- Cartes par polluants (O3, NO2, PM10, PM25) - Aymeric

### Etude de l'origine de la pollution de l'air par regression

- Préprocessing (réduction de dimension, nettoyage)
- Fit deRegressions linéaires/Lasso/Données de panel
- dans un second temps, garder que les stations urbaines et périurbaines ? (pas les rurales)

### Etude de l'origine de la pollution de l'air par ML

- Préprocessing (réduction de dimension, nettoyage)
- Etude via CART/Random Forest (nbre de données suffisantes ?)
