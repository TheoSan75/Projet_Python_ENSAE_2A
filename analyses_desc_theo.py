#########################################
#####  Analyses descriptives - Théo #####
#########################################
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt

# Import des données
data_air = pd.read_csv("Projet_Python_ENSAE_2A/data/raw_data/Export Moy. annuelle - 20251120135910 - 2022-01-01 00_00 - 2022-12-31 23_00.csv")
data_villes = pd.read_csv("Projet_Python_ENSAE_2A/data/raw_data/data.csv", sep=";")
data_tourisme = pd.read_csv("Projet_Python_ENSAE_2A/data/raw_data/BDD_tourisme_communes_2022.csv", sep=";")

# Jointure des données des ville et du tourisme
data_villes.rename(columns={'Code': "CODGEO"}, inplace=True)
print(data_villes.columns)
print(data_tourisme.columns)
data_join = data_villes.merge(data_tourisme, on="CODGEO", how="left")
print(data_villes.shape, data_tourisme.shape, data_join.shape)

# On sauvegarde le dataset joint
data_join.to_csv("Projet_Python_ENSAE_2A/data/processed_data/data_villes_tourisme.csv", index=False)

# On vérifie que la jointure a bien fonctionné
print(data_villes.shape, data_tourisme.shape, data_join.shape)


