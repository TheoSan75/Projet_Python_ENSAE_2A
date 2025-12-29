import pandas as pd
import time
import requests

GOV_API = "https://api-adresse.data.gouv.fr/reverse"
HEADERS = {"User-Agent": "geodair-geocoder"}
SLEEP_SEC = 0.12


def reverse_insee(lat, lon, timeout=10):

    """
    Prend en argument une latitude et une longitude,
    et retourne la commune où se trouve ces coordonnées, ainsi que son code commune INSEE,
    en interrogeant l'API de data.gouv.fr.
    """

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

    """
    Ajoute au dataframe geodair une colonne 'Ville' et une colonne 'CODGEO'
    contenant respectivement la ville où se situe chaque station et son code commune INSEE.
    """

    coords_unique = geodair[['Latitude', 'Longitude']].drop_duplicates()
    result = {}

    for idx, row in coords_unique.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        city, code_insee = reverse_insee(lat, lon)

        result[(lat, lon)] = (city, code_insee)

        print(city, code_insee)

        time.sleep(SLEEP_SEC)

    geodair['Ville'] = geodair.apply(lambda r: result[(r['Latitude'], r['Longitude'])][0], axis=1)
    geodair['CODGEO'] = geodair.apply(lambda r: result[(r['Latitude'], r['Longitude'])][1], axis=1)
