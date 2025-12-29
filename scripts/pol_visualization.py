import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from cartiflette import carti_download


polluants = ["NOX as NO2", "O3", "PM2.5", "PM10"]
seuil_OMS = {"NOX as NO2": 10, "O3": 60, "PM2.5": 5, "PM10": 15}


def visualization(geodair):

    """
    Affiche à partir du dataframe geodair, pour chacun des 4 polluants considérés, 
    une carte des villes de France métropolitaine où se situe au moins une station de mesure pour ce polluant,
    colorées en fonction de la quantité de ce polluant présente dans l'air.
    """

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

    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    axes = axes.flatten()

    for i, polluant in enumerate(polluants):

        geodair_polluant = (
            geodair.loc[geodair["Polluant"] == polluant, :]
            .groupby(["CODGEO", "Latitude_commune", "Longitude_commune"])
            .agg({"valeur brute": "mean"})
            .reset_index()
        )

        geodair_gdf = gpd.GeoDataFrame(
            geodair_polluant,
            geometry=gpd.points_from_xy(geodair_polluant["Longitude_commune"], geodair_polluant["Latitude_commune"]),
            crs="EPSG:4326"
        )

        france.plot(ax=axes[i], edgecolor="black", facecolor="none")

        geodair_gdf.plot(
            ax=axes[i],
            column="valeur brute",
            cmap="coolwarm",
            markersize=20,
            legend=True,
            legend_kwds={"label": f"Valeur brute de {polluant}", "orientation": "horizontal"}
        )

        axes[i].set_title(f"Carte de la pollution mesurée en {polluant}")

    plt.tight_layout()
    plt.show()



def visualization_OMS(geodair):

    """
    Affiche à partir du dataframe geodair, pour chacun des 4 polluants considérés, 
    une carte des villes de France métropolitaine où se situe au moins une station de mesure pour ce polluant,
    colorées en fonction du dépassement où non du seuil recommandé par l'OMS.
    """

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

    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    axes = axes.flatten()

    cmap = mcolors.ListedColormap(['green', 'red'])
    norm = mcolors.BoundaryNorm([0, 0.5, 1], 2)

    for i, polluant in enumerate(polluants):

        geodair_polluant = (
            geodair.loc[geodair["Polluant"] == polluant, :]
            .groupby(["CODGEO", "Latitude_commune", "Longitude_commune"])
            .agg({"valeur brute": "mean"})
            .reset_index()
        )

        geodair_polluant["dépassement"] = geodair_polluant["valeur brute"] >= seuil_OMS[polluant]

        geodair_gdf = gpd.GeoDataFrame(
            geodair_polluant,
            geometry=gpd.points_from_xy(geodair_polluant["Longitude_commune"], geodair_polluant["Latitude_commune"]),
            crs="EPSG:4326"
        )

        france.plot(ax=axes[i], edgecolor="black", facecolor="none")

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

        axes[i].set_title(f"Pollution en {polluant} (Seuil OMS: {seuil_OMS[polluant]} \u03BCg/m³)")

    plt.tight_layout()
    plt.show()
