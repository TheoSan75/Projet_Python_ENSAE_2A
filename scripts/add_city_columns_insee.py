import pandas as pd
import time
import requests

GOV_API = "https://api-adresse.data.gouv.fr/reverse"
HEADERS = {"User-Agent": "geodair-geocoder"}
SLEEP_SEC = 0.12


def reverse_insee(lat, lon, timeout=10):
    params = {"lat": lat, "lon": lon}
    try:
        r = requests.get(GOV_API, params=params, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        feats = data.get("features", [])
        if not feats:
            return None, None

        props = feats[0].get("properties", {})
        city = props.get("city")
        code_insee = props.get("citycode")

        return city, code_insee

    except Exception:
        return None, None


def add_city_codes(geodair):
    # On ne garde que les coordonnées uniques
    coords_unique = geodair[['Latitude', 'Longitude']].drop_duplicates()

    # On va stocker les résultats ici
    result = {}

    for idx, row in coords_unique.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        city, code_insee = reverse_insee(lat, lon)

        result[(lat, lon)] = (city, code_insee)

        print(city, code_insee)

        time.sleep(SLEEP_SEC)  # être "gentil" avec l’API

    # On crée deux colonnes via une map vectorisée
    geodair['Ville'] = geodair.apply(lambda r: result[(r['Latitude'], r['Longitude'])][0], axis=1)
    geodair['CODGEO'] = geodair.apply(lambda r: result[(r['Latitude'], r['Longitude'])][1], axis=1)


def add_city_coords(geodair):

    communes = pd.read_csv("data/raw_data/20230823-communes-departement-region.csv")

    communes = communes[["code_commune_INSEE", "latitude", "longitude"]].rename(columns={
        "code_commune_INSEE": "CODGEO",
        "latitude": "Latitude_commune",
        "longitude": "Longitude_commune"
    })

    geodair = geodair.merge(
        communes,
        on="CODGEO",
        how="left"
    )

    return geodair


def add_city_columns(input_filename, output_filename):

    geodair = pd.read_csv("data/raw_data/" + input_filename, sep=";")

    add_city_codes(geodair)
    geodair = add_city_coords(geodair)

    geodair.to_csv("data/processed_data/" + output_filename, index=False)
