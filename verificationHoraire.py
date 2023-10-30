import pandas as pd
import datetime
import numpy as np

#FICHIER PREMIERE VERIFICATION
#
#

# Chargement des fichiers GTFS dans des df
stops = pd.read_csv("GTFS/stops.txt", delimiter=",")
routes = pd.read_csv("GTFS/routes.txt", delimiter=",")
datas_2023_10_26 = pd.read_csv("Trip_By_Day/2023-10-26.csv", delimiter=",")
datas_2023_10_27 = pd.read_csv("Trip_By_Day/2023-10-27.csv", delimiter=",")
datas_2023_10_28 = pd.read_csv("Trip_By_Day/2023-10-28.csv", delimiter=",")
stop_times = pd.read_csv("GTFS/stop_times.txt", delimiter=",")


def recupRouteId(tripId: str,data_in):
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(data_in, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    result = result[result["trip_id"].astype(str) == str(tripId)]
    print("Trajet " + str(result["route_id"].iloc[0]))


def miseEnForme(routeId: str, tripId: str, directionId: int,data_in):
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(data_in, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={'arrival_time': 'arrival_time_reel'})
    result = result.rename(columns={'departure_time': 'departure_time_reel'})

    result = result[result["route_id"].astype(str) == str(routeId)]

    result = result[result["trip_id"].astype(str) == str(tripId)]

    result = result[result["direction_id"] == directionId]

    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    result = pd.merge(result, stop_times, on=["trip_id", "stop_id"], how="inner")

    columns_to_display = [
        "trip_id",
        "stop_id",
        "stop_name",
        "route_long_name",
        "direction_id",
        "arrival_delay",
        "arrival_time_reel",
        "departure_delay",
        "departure_time_reel",
    ]
    for index, row in result.iterrows():
        result.loc[index, "arrival_time_reel"] = datetime.datetime.fromtimestamp(
            row["arrival_time_reel"]
        )
        result.loc[index, "departure_time_reel"] = datetime.datetime.fromtimestamp(
            row["departure_time_reel"]
        )
    print("Trajet " + str(result["route_long_name"].iloc[0]))
    result = result.sort_values(by="departure_time_reel")
    result = result.drop_duplicates(subset=["trip_id", "stop_id"], keep="last")
    for index, row in result.iterrows():
        print(
            "départ à           "
            + str(row["departure_time_reel"])
            + "     normalement prévue à "
            + str(row["departure_time"])
            + "          de l'arrêt "
            + str(row["stop_name"])
        )


#recupRouteId("25-T1-1-A-045244",datas_2023_10_28)
#miseEnForme("4-T1", "25-T1-1-A-045244", 0,datas_2023_10_28)

#TRIP/ROUTE diff semaine & week-end
#
#

class TripParJour:
    def __init__(self,data,date):
        self.data = data
        self.date=date

# départ en avance
def routeParTripParJour(data_in):
    date=str(datetime.datetime.fromtimestamp(data_in["departure_time"].iloc[0]))[:10]
    print(date)
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(data_in, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")
    result = result.drop(columns=["arrival_time","departure_time","stop_id","direction_id","service_id","shape_id","trip_headsign","trip_short_name","agency_id","route_short_name"])
    #columns restantes : [trip_id,arrival_delay,departure_delay,route_id,route_long_name]

    agg_funcs = {
    'trip_id': 'count',
    'arrival_delay': 'mean',
    'departure_delay': 'mean',
    'route_long_name': 'first',
    'route_type': 'first'
    }

    # Utilisez la méthode .groupby() pour regrouper par "route_id" et appliquer les opérations spécifiées.
    result = result.groupby('route_id').agg(agg_funcs).reset_index()
    result = result.rename(columns={'trip_id': 'trip_id_count'})
    
    # traduction de la colonne route_type de int à string : 0=Tram, 3=Bus
    result["route_type"] = result["route_type"].astype(str)
    for index, row in result.iterrows():
        if str(row["route_type"]) == "3":
            result.loc[index, "route_type"] = "Bus"
        if str(row["route_type"]) == "0":
            result.loc[index, "route_type"] = "Tramway"

    print(result)
    return TripParJour(result,date)

df1=routeParTripParJour(datas_2023_10_27) # vendredi
df2=routeParTripParJour(datas_2023_10_28) # samedi

# fonction renvoyant toutes les lignes avec une moyenne de départ en avance au dessus de la normale
def departEnAvance(data1):
    for index, row in data1.data.iterrows():
        if row["departure_delay"] < 0:
            print(
                "Le "
                + data1.date
                + " le trajet "
                + str(row["route_long_name"])
                + " en "
                + str(row["route_type"])
                + " est parti en avance d'en moyenne "
                + str(int((-1)*row["departure_delay"]))
                + " secondes."
            )
    return 0

#departEnAvance(df1)

def diffSemaineEtWeekend(data_1,data_2):
    res1 = data_1.data
    res2 = data_2.data

    return 0

diffSemaineEtWeekend(df1,df2)