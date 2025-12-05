from geopy.geocoders import Nominatim
import pandas as pd
import time



def add_city_codes(geodair, geolocator):

    n, _ = geodair.shape
    coords = [(geodair.loc[i, "Latitude"], geodair.loc[i, "Longitude"]) for i in range(n)]

    cities = []
    codgeo = []
    possible_fields = ['city', 'town', 'village', 'municipality', 'hamlet']

    for i in range(n):
        lat, lon = coords[i]
        location = geolocator.reverse((lat, lon), exactly_one=True)
        address = location.raw['address']

        city = None
        for field in possible_fields:
            if field in address:
                city = address[field]
                break

        code_insee = address.get('citycode')

        cities.append(city)
        codgeo.append(code_insee)
        time.sleep(1)

    n_none = 0
    n = len(cities)
    for i in range(n_none):
        if cities[i] == None:
            n_none += 1
    if n_none > 0:
        print("Warning: " + n_none + " cities not found")

    geodair["Ville"] = pd.Series(cities)
    geodair["CODGEO"] = pd.Series(codgeo)



def add_city_coords(geodair, geolocator):

    def geocode_city(city):
        try:
            loc = geolocator.geocode(city + ", France")
            if loc:
                return pd.Series([loc.latitude, loc.longitude])
        except:
            pass
        return pd.Series([None, None])

    geodair[["Latitude ville", "Longitude ville"]] = geodair["Ville"].apply(geocode_city)



def add_city_columns(input_filename, output_filename):

    geolocator = Nominatim(user_agent="geoapi", timeout = 10)
    geodair = pd.read_csv("data/raw_data/" + input_filename, sep=";")

    add_city_codes(geodair, geolocator)
    add_city_coords(geodair, geolocator)

    geodair.to_csv("data/processed_data/" + output_filename, index=False)