import streamlit as st
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import os

nom_GTFS="GTFS_2023_11_07"

# Chargement des fichiers GTFS dans des df
stops = pd.read_csv(f"{nom_GTFS}/stops.txt", delimiter=",")
routes = pd.read_csv(f"{nom_GTFS}/routes.txt", delimiter=",")


fichiers_csv = os.listdir("Trip_By_Day")
for fichier_csv in fichiers_csv:
    # garde que la date du nom du fichier
    date_str = fichier_csv.split('.')[0].replace('-', '_')
    # nouveau nom dataframe
    nom_dataframe = f"datas_{date_str}"
    # création d'un dataframe par fichier csv
    globals()[nom_dataframe] = pd.read_csv(os.path.join("Trip_By_Day", fichier_csv), delimiter=",")

stop_times = pd.read_csv(f"{nom_GTFS}/stop_times.txt", delimiter=",")

class TripParJour:
    def __init__(self, data, date):
        self.data = data
        self.date = date


def routeParTripParJour(data_in):
    date = str(datetime.datetime.fromtimestamp(data_in["departure_time"].iloc[0]))[:10]
    trips = pd.read_csv(f"{nom_GTFS}/trips.txt", delimiter=",")
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


# fonction renvoyant toutes les lignes avec une moyenne de départ en avance au dessus de la normale
def departEnAvance(data1):
    print("\nFonction énumérant les lignes parties en avances :")
    df_final=pd.DataFrame(columns=data1.data.columns)
    for index, row in data1.data.iterrows():
        if row["departure_delay_mean"] < 0:
            df_final.loc[index]=row
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
    st.dataframe(df_final)
    return 0

def graphJourneeByRoute(routeId: str, directionId: int, data_in):
    print(
        "\nAffichage histogramme des passages sur une route en particulier sur une journée :"
    )
    trips = pd.read_csv(f"{nom_GTFS}/trips.txt", delimiter=",")
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


    st.write(f"Histogramme des heures de départ sur la ligne {routeId.replace('4-', '')}")

    # Créer les histogrammes avec Matplotlib
    fig, ax = plt.subplots()
    # création un histogramme des minutes depuis minuit
    ax.hist(
        result["departure_hour"],
        bins=range(0, 27),
        alpha=0.5,
        rwidth=0.9,
        align="left",
        label="Histogramme Dates prévues",
    )
    ax.hist(
        result["departure_hour_reel"],
        bins=range(0, 27),
        alpha=0.5,
        rwidth=0.9,
        align="left",
        label="Histogramme Dates réelles",
    )

    ax.legend()

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

    ax.set_xlabel("Heure de la journée")
    ax.set_ylabel("Fréquence de passage")

    # affichage du graphique dans Streamlit
    st.pyplot(fig)
    return 0

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fin fonctions, passage section Menu
# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# Menu pour choisir la fonction à utiliser
if __name__ == "__main__":
    st.sidebar.title("Menu")

    # date picker
    selected_date = st.sidebar.date_input("Sélectionner une date", datetime.datetime(2023, 10, 27))
    date_str = selected_date.strftime('%Y_%m_%d')
    nom_dataframe = f"datas_{date_str}"
    
    # ligne de trajet picker
    choix_routes = pd.read_csv(f"{nom_GTFS}/routes.txt", delimiter=",")
    ligne_trajet = st.sidebar.selectbox("Sélectionne une Ligne Divia", choix_routes["route_long_name"])
    print(choix_routes[choix_routes["route_long_name"]==ligne_trajet].index[0])
    index = choix_routes[choix_routes["route_long_name"]==ligne_trajet].index[0]

    selected_id = choix_routes.loc[index, "route_id"]
    print(selected_id)
    # Ajoute un sélecteur pour choisir la fonctionnalité
    fonctionnalite = st.sidebar.selectbox("Sélectionne une fonctionnalité", ["Afficher DataFrame", "Tracer Graphique"])

    # Appelle la fonction appropriée en fonction de la sélection
    if fonctionnalite == "Afficher DataFrame":
        if nom_dataframe in globals():
            departEnAvance(routeParTripParJour(globals()[nom_dataframe]))
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")
    elif fonctionnalite == "Tracer Graphique":
        if nom_dataframe in globals():
            graphJourneeByRoute(selected_id, 0, globals()[nom_dataframe])
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")