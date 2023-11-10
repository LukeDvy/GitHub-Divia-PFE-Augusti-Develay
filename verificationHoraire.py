import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt

# FICHIER PREMIERE VERIFICATION
#
#

# Chargement des fichiers GTFS dans des df
stops = pd.read_csv("GTFS/stops.txt", delimiter=",")
routes = pd.read_csv("GTFS/routes.txt", delimiter=",")
datas_2023_10_26 = pd.read_csv("Trip_By_Day/2023-10-26.csv", delimiter=",")
datas_2023_10_27 = pd.read_csv("Trip_By_Day/2023-10-27.csv", delimiter=",")
datas_2023_10_28 = pd.read_csv("Trip_By_Day/2023-10-28.csv", delimiter=",")
datas_2023_10_31 = pd.read_csv("Trip_By_Day/2023-10-31.csv", delimiter=",")
datas_2023_11_09 = pd.read_csv("Trip_By_Day/2023-11-09.csv", delimiter=",")


stop_times = pd.read_csv("GTFS/stop_times.txt", delimiter=",")


def recupRouteId(tripId: str, data_in):
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(data_in, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    result = result[result["trip_id"].astype(str) == str(tripId)]
    print("Trajet " + str(result["route_id"].iloc[0]))


def miseEnForme(routeId: str, tripId: str, directionId: int, data_in):
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(data_in, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={"arrival_time": "arrival_time_reel"})
    result = result.rename(columns={"departure_time": "departure_time_reel"})

    result = result[result["route_id"].astype(str) == str(routeId)]

    result = result[result["trip_id"].astype(str) == str(tripId)]
    ##result = result[result["stop_id"].astype(str) == str(tripId)] #####

    result = result[result["direction_id"] == directionId]

    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    result = pd.merge(
        result, stop_times, on=["trip_id", "stop_id"], how="inner"
    )  # essayer right pour afficher les données manquantes dans GTFS-RT

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


# recupRouteId("13-T2-13-1-085531",datas_2023_10_31)
# miseEnForme("4-T1", "25-T1-1-A-045244", 0,datas_2023_10_28)
# miseEnForme("4-T2", "13-T2-13-1-085531", 1,datas_2023_10_31)


# TRIP/ROUTE diff semaine & week-end
#
#


class TripParJour:
    def __init__(self, data, date):
        self.data = data
        self.date = date


def routeParTripParJour(data_in):
    date = str(datetime.datetime.fromtimestamp(data_in["departure_time"].iloc[0]))[:10]
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(data_in, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")
    result = result.drop(
        columns=[
            "arrival_time",
            "departure_time",
            "stop_id",
            "direction_id",
            "service_id",
            "shape_id",
            "trip_headsign",
            "trip_short_name",
            "agency_id",
            "route_short_name",
        ]
    )
    # columns restantes : [trip_id,arrival_delay,departure_delay,route_id,route_long_name]
    result = result.rename(columns={"arrival_delay": "arrival_delay_mean"})
    result = result.rename(columns={"departure_delay": "departure_delay_mean"})
    result["arrival_delay_min"] = result["arrival_delay_mean"]
    result["departure_delay_min"] = result["departure_delay_mean"]
    result["arrival_delay_max"] = result["arrival_delay_mean"]
    result["departure_delay_max"] = result["departure_delay_mean"]

    agg_funcs = {
        "trip_id": "count",
        "arrival_delay_mean": "mean",
        "arrival_delay_min": "min",
        "arrival_delay_max": "max",
        "departure_delay_mean": "mean",
        "departure_delay_min": "min",
        "departure_delay_max": "max",
        "route_long_name": "first",
        "route_type": "first",
    }

    # utilisation de  la méthode .groupby() pour regrouper par "route_id" et appliquer les opérations spécifiée
    result = result.groupby("route_id").agg(agg_funcs).reset_index()
    result = result.rename(columns={"trip_id": "trip_id_count"})

    # traduction de la colonne route_type de int à string : 0=Tram, 3=Bus
    result["route_type"] = result["route_type"].astype(str)
    for index, row in result.iterrows():
        if str(row["route_type"]) == "3":
            result.loc[index, "route_type"] = "Bus"
        if str(row["route_type"]) == "0":
            result.loc[index, "route_type"] = "Tramway"

    # print(result)
    return TripParJour(result, date)


df1 = routeParTripParJour(datas_2023_10_27)  # vendredi
df2 = routeParTripParJour(datas_2023_10_31)  # samedi


# fonction renvoyant toutes les lignes avec une moyenne de départ en avance au dessus de la normale
def departEnAvance(data1):
    print("\nFonction énumérant les lignes parties en avances :")
    for index, row in data1.data.iterrows():
        if row["departure_delay_mean"] < 0:
            print(
                "Le "
                + data1.date
                + " le trajet "
                + str(row["route_long_name"])
                + " en "
                + str(row["route_type"])
                + " est parti en avance d'en moyenne "
                + str(int((-1) * row["departure_delay_mean"]))
                + " secondes. Avec, un départ en avance max de "
                + str(int((-1) * row["departure_delay_min"]))
                + " secondes.\n"
            )
    return 0


departEnAvance(df2)


def diffDeuxDates(data_1, data_2):
    print("\nFonction énumérant les différences entre deux dates :")

    res1 = data_1.data
    res2 = data_2.data
    print(
        str(len(res1))
        + " trajets le "
        + str(data_1.date)
        + " contre "
        + str(len(res2))
        + " trajets le "
        + str(data_2.date)
    )
    result_exclu = pd.merge(
        res1, res2, on="route_id", how="outer", suffixes=("_df1", "_df2")
    )
    result_exclu = result_exclu.loc[
        result_exclu["trip_id_count_df1"].isna()
        | result_exclu["trip_id_count_df2"].isna()
    ]
    for index, row in result_exclu.iterrows():
        if str(row["trip_id_count_df1"]) == "nan":
            print(
                "Le trajet en "
                + str(row["route_type_df2"])
                + " sur la ligne "
                + str(row["route_long_name_df2"])
                + " est de passage le "
                + str(data_2.date)
                + " et non le "
                + str(data_1.date)
            )
        else:
            print(
                "Le trajet en "
                + str(row["route_type_df1"])
                + " sur la ligne "
                + str(row["route_long_name_df1"])
                + " est de passage le "
                + str(data_1.date)
                + " et non le "
                + str(data_2.date)
            )
    return 0


diffDeuxDates(df1, df2)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonctions d'affichage de graphiques
# ------------------------------------------------------------------------------------------------------------------------------------------------------------


def graphJourneeByRoute(routeId: str, directionId: int, data_in):
    print(
        "\nAffichage histogramme des passages sur une route en particulier sur une journée :"
    )
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(data_in, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={"arrival_time": "arrival_time_reel"})
    result = result.rename(columns={"departure_time": "departure_time_reel"})

    result = result[result["route_id"].astype(str) == str(routeId)]

    result = result[result["direction_id"] == directionId]

    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    result = pd.merge(
        result, stop_times, on=["trip_id", "stop_id"], how="inner"
    )  # essayer right pour afficher les données manquantes dans GTFS-RT

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

    result["departure_time_reel"] = pd.to_datetime(result["departure_time_reel"])

    # exctraction de l'heure
    result["departure_hour"] = result["departure_time"].str.extract(r"(\d{2}):")
    result["departure_hour_reel"] = result["departure_time_reel"].dt.hour

    # modification du type en tant que datetime
    result["departure_hour"] = result["departure_hour"].astype(int)
    result["departure_hour_reel"] = result["departure_hour_reel"].astype(int)

    # création un histogramme des minutes depuis minuit
    plt.hist(
        result["departure_hour"],
        bins=range(0, 27),
        alpha=0.5,
        rwidth=0.9,
        align="left",
        label="Histogramme Dates prévues",
    )
    plt.hist(
        result["departure_hour_reel"],
        bins=range(0, 27),
        alpha=0.5,
        rwidth=0.9,
        align="left",
        label="Histogramme Dates réelles",
    )

    plt.legend()

    # configuration l'axe des abscisses pour afficher les heures de la journée
    ax = plt.gca()

    # Set des abscisses
    abs_labels = [
        f"{i%24:02d}:00" for i in range(26)
    ]  # permet l'affichage correcte des abscisses : ex : 01h avec deux chiffres avec ':02d'. en fstring, car sinon affiche les '{}'
    ax.set_xticks(
        range(0, 26)
    )  # place une abscisses toutes les 60 minutes sur une journée de 24 heures
    ax.set_xticklabels(
        abs_labels, rotation=45
    )  # rotation des labels pour pas qu'ils soient superposés

    plt.xlabel("Heure de la journée")
    plt.ylabel("Fréquence de passage")
    plt.title(
        "Histogramme des heures de départ sur la ligne "
        + str(routeId.replace("4-", ""))
    )

    plt.show()
    return 0


graphJourneeByRoute("4-T2", 0, datas_2023_10_27)


def graphJourneeByRouteAndStop(stopId: str, data_in):
    print(
        "\nAffichage histogramme des passages à un arrêt en particulier sur une journée :"
    )
    trips = pd.read_csv("GTFS/trips.txt", delimiter=",")
    result = pd.merge(data_in, stops, on="stop_id", how="inner")
    trips = trips.drop(columns="direction_id")
    result = pd.merge(result, trips, on="trip_id", how="inner")
    result = pd.merge(result, routes, on="route_id", how="inner")

    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={"arrival_time": "arrival_time_reel"})
    result = result.rename(columns={"departure_time": "departure_time_reel"})

    # result = result[result["direction_id"] == directionId]
    result = result[result["stop_id"] == stopId]

    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    result = pd.merge(
        result, stop_times, on=["trip_id", "stop_id"], how="inner"
    )  # essayer right pour afficher les données manquantes dans GTFS-RT

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

    result["departure_hour"] = (
        result["departure_time"].str.extract(r"(\d{2}):").astype(int)
    )
    result = result[result["departure_hour"] < 24]
    result = result.drop(columns="departure_hour")

    # modification du type en tant que datetime
    result["departure_time_reel"] = pd.to_datetime(result["departure_time_reel"])
    result["departure_time"] = pd.to_datetime(result["departure_time"])
    
    # suppression des valeurs en dehors du champ correcte des heures
    result = result[
        (result["departure_time_reel"].dt.hour >= 0)
        & (result["departure_time_reel"].dt.hour <= 23)
    ]
    result = result[
        (result["departure_time"].dt.hour >= 0)
        & (result["departure_time"].dt.hour <= 23)
    ]

    result["departure_time_reel"] = (
        result["departure_time_reel"].dt.hour * 60
        + result["departure_time_reel"].dt.minute
    )
    result["departure_time"] = (
        result["departure_time"].dt.hour * 60 + result["departure_time"].dt.minute
    )

    # création un histogramme des minutes depuis minuit
    plt.hist(
        result["departure_time_reel"],
        bins=24,
        alpha=0.5,
        rwidth=0.9,
        align="left",
        label="Histogramme Dates réelles",
    )
    plt.hist(
        result["departure_time"],
        bins=24,
        alpha=0.5,
        rwidth=0.9,
        align="left",
        label="Histogramme Dates prévues",
    )

    plt.legend()

    # configuration l'axe des abscisses pour afficher les heures de la journée
    ax = plt.gca()

    # Set des abscisses
    abs_labels = [
        f"{i:02d}:00" for i in range(24)
    ]  # permet l'affichage correcte des abscisses : ex : 01h avec deux chiffres avec ':02d'. en fstring, car sinon affiche les '{}'
    ax.set_xticks(
        range(0, 1440, 60)
    )  # place une abscisses toutes les 60 minutes sur une journée de 24 heures
    ax.set_xticklabels(
        abs_labels, rotation=45
    )  # rotation des labels pour pas qu'ils soient superposés

    plt.xlabel("Heure de la journée")
    plt.ylabel("Fréquence de passage")
    plt.title(
        "Histogramme des heures de départ sur la ligne "
        + str(result["route_id"].iloc[0]).replace("4-", "")
        + " à l'arrêt "
        + str(result["stop_name"].iloc[0])
    )

    plt.show()
    return 0


graphJourneeByRouteAndStop("4-1457", datas_2023_11_09)
