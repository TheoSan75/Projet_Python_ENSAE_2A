import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from cartiflette import carti_download

# Liste des polluants à cartographier
polluants = ["NOX as NO2", "O3", "PM2.5", "PM10"]
seuil_OMS = {"NOX as NO2": 10, "O3": 60, "PM2.5": 5, "PM10": 15}


def visualization(geodair):

    # Téléchargement des frontières de la France (une seule fois)
    france = carti_download(
        values=["France"],
        crs=4326,
        borders="REGION",
        vectorfile_format="geojson",
        simplification=50,
        filter_by="FRANCE_ENTIERE",
        source="EXPRESS-COG-CARTO-TERRITOIRE",
        year=2022
    )
    france = france.loc[france['INSEE_REG'] > 10]

    # Création d'une figure avec 4 sous-graphiques (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    axes = axes.flatten()  # Pour itérer facilement

    # Boucle sur chaque polluant
    for i, polluant in enumerate(polluants):
        # Filtrage et agrégation pour le polluant actuel
        geodair_polluant = (
            geodair.loc[geodair["Polluant"] == polluant, :]
            .groupby(["CODGEO", "Latitude_commune", "Longitude_commune"])
            .agg({"valeur brute": "mean"})
            .reset_index()
        )

        # Création du GeoDataFrame pour les points
        geodair_gdf = gpd.GeoDataFrame(
            geodair_polluant,
            geometry=gpd.points_from_xy(geodair_polluant["Longitude_commune"], geodair_polluant["Latitude_commune"]),
            crs="EPSG:4326"
        )

        # Tracé des frontières de la France
        france.plot(ax=axes[i], edgecolor="black", facecolor="none")

        # Tracé des points avec une couleur dépendant de "valeur brute"
        geodair_gdf.plot(
            ax=axes[i],
            column="valeur brute",
            cmap="coolwarm",
            markersize=20,
            legend=True,
            legend_kwds={"label": f"Valeur brute de {polluant}", "orientation": "horizontal"}
        )

        # Titre du sous-graphe
        axes[i].set_title(f"Carte de la pollution mesurée en {polluant}")

    # Ajustement de l'espacement entre les sous-graphiques
    plt.tight_layout()
    plt.show()



def visualization_OMS(geodair):

    # Téléchargement des frontières de la France
    france = carti_download(
        values=["France"],
        crs=4326,
        borders="REGION",
        vectorfile_format="geojson",
        simplification=50,
        filter_by="FRANCE_ENTIERE",
        source="EXPRESS-COG-CARTO-TERRITOIRE",
        year=2022
    )
    france = france.loc[france['INSEE_REG'] > 10]

    # Création d'une figure avec 4 sous-graphiques (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    axes = axes.flatten()

    # Palette de couleurs discrète (rouge = dépassement, vert = conforme)
    cmap = mcolors.ListedColormap(['green', 'red'])
    norm = mcolors.BoundaryNorm([0, 0.5, 1], 2)  # 0->vert, 1->rouge

    # Boucle sur chaque polluant
    for i, polluant in enumerate(polluants):
        # Filtrage et agrégation
        geodair_polluant = (
            geodair.loc[geodair["Polluant"] == polluant, :]
            .groupby(["CODGEO", "Latitude_commune", "Longitude_commune"])
            .agg({"valeur brute": "mean"})
            .reset_index()
        )
        # Ajout d'une colonne binaire pour le seuil
        geodair_polluant["dépassement"] = geodair_polluant["valeur brute"] >= seuil_OMS[polluant]

        # Création du GeoDataFrame
        geodair_gdf = gpd.GeoDataFrame(
            geodair_polluant,
            geometry=gpd.points_from_xy(geodair_polluant["Longitude_commune"], geodair_polluant["Latitude_commune"]),
            crs="EPSG:4326"
        )

        # Tracé des frontières
        france.plot(ax=axes[i], edgecolor="black", facecolor="none")

        # Tracé des points avec couleur selon le seuil
        geodair_gdf.plot(
            ax=axes[i],
            column="dépassement",
            cmap=cmap,
            norm=norm,
            markersize=20,
            legend=True,
            legend_kwds={
                "loc": "lower right",
                "title": f"Dépassement du seuil OMS ({seuil_OMS[polluant]} \u03BCg/m³)",
                "labels": ["Conforme", "Dépassement"]
            }
        )

        # Titre
        axes[i].set_title(f"Pollution en {polluant} (Seuil OMS: {seuil_OMS[polluant]} \u03BCg/m³)")

    plt.tight_layout()
    plt.show()
