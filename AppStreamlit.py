import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import os
import pytz

nom_GTFS = "GTFS_2023_11_07"

# Définition du fuseau horaire CET
original_timezone = pytz.timezone('UTC')
cet_timezone = pytz.timezone('CET')

# Chargement des fichiers GTFS dans des df
stops = pd.read_csv(f"{nom_GTFS}/stops.txt", delimiter=",")
routes = pd.read_csv(f"{nom_GTFS}/routes.txt", delimiter=",")


fichiers_csv = os.listdir("Trip_By_Day")
for fichier_csv in fichiers_csv:
    # garde que la date du nom du fichier
    date_str = fichier_csv.split(".")[0].replace("-", "_")
    # nouveau nom dataframe
    nom_dataframe = f"datas_{date_str}"
    # création d'un dataframe par fichier csv
    globals()[nom_dataframe] = pd.read_csv(
        os.path.join("Trip_By_Day", fichier_csv), delimiter=","
    )

stop_times = pd.read_csv(f"{nom_GTFS}/stop_times.txt", delimiter=",")


class TripParJour:
    def __init__(self, data, date):
        self.data = data
        self.date = date


def routeParTripParJour(data_in):
    date = str((original_timezone.localize(datetime.fromtimestamp(data_in["departure_time"].iloc[0]))).astimezone(cet_timezone))[:10]
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
    df_final = pd.DataFrame(columns=data1.data.columns)
    for index, row in data1.data.iterrows():
        if row["departure_delay_mean"] < 0:
            df_final.loc[index] = row
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


def graphJourneeByRoute(routeId: str, directionId: int, data_in, selected_date):
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
        result.loc[index, "arrival_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["arrival_time_reel"]
        ))).astimezone(cet_timezone)
        result.loc[index, "departure_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["departure_time_reel"]
        ))).astimezone(cet_timezone)
    try:
        print("Trajet " + str(result["route_long_name"].iloc[0]))
    except:
        st.warning(f"Aucune données trouvées pour la date {selected_date}")
        return 0
    result = result.sort_values(by="departure_time_reel")
    result = result.drop_duplicates(subset=["trip_id", "stop_id"], keep="last")

    result["departure_time_reel"] = pd.to_datetime(result["departure_time_reel"])

    # exctraction de l'heure
    result["departure_hour"] = result["departure_time"].str.extract(r"(\d{2}):")
    result["departure_hour_reel"] = result["departure_time_reel"].dt.hour

    # modification du type en tant que datetime
    result["departure_hour"] = result["departure_hour"].astype(int)
    result["departure_hour_reel"] = result["departure_hour_reel"].astype(int)

    # affichage titre histogramme
    st.markdown(
        f"<h4 style='text-align: center;'>Histogramme des heures de départ sur la Ligne "
        f"{routeId.replace('4-', '')}</h4>",
        unsafe_allow_html=True,
    )

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


def graphJourneeByRouteAndStop(stopId: str, data_in, selected_date):
    print(
        "\nAffichage histogramme des passages à un arrêt en particulier sur une journée :"
    )
    trips = pd.read_csv(f"{nom_GTFS}/trips.txt", delimiter=",")
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
        result.loc[index, "arrival_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["arrival_time_reel"]
        ))).astimezone(cet_timezone)
        result.loc[index, "departure_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["departure_time_reel"]
        ))).astimezone(cet_timezone)
    try:
        print("Trajet " + str(result["route_long_name"].iloc[0]))
    except:
        st.warning(f"Aucune données trouvées pour la date {selected_date}")
        return 0
    result = result.sort_values(by="departure_time_reel")
    result = result.drop_duplicates(subset=["trip_id", "stop_id"], keep="last")

    result["departure_time_reel"] = pd.to_datetime(result["departure_time_reel"])

    # exctraction de l'heure
    result["departure_hour"] = result["departure_time"].str.extract(r"(\d{2}):")
    result["departure_hour_reel"] = result["departure_time_reel"].dt.hour

    # modification du type en tant que datetime
    result["departure_hour"] = result["departure_hour"].astype(int)
    result["departure_hour_reel"] = result["departure_hour_reel"].astype(int)

    # affichage titre histogramme
    st.markdown(
        f"<h5 style='text-align: center;'>Histogramme des heures de départ sur la Ligne "
        f"{str(result['route_id'].iloc[0]).replace('4-', '')} à l'arrêt "
        f"{str(result['stop_name'].iloc[0])}</h5>",
        unsafe_allow_html=True,
    )

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

def tpsAttente(stopId: str, data_in, selected_date):
    print(
        "\nAffichage temps attente entre deux véhicules par plage horaire, à un arrêt en particulier :"
    )
    result=data_in
    trips = pd.read_csv(f"{nom_GTFS}/trips.txt", delimiter=",")
    
    stopRoute = pd.merge(stops, stop_times, on="stop_id", how="inner")
    stopRoute = pd.merge(stopRoute, trips, on="trip_id", how="inner")
    stopRoute = pd.merge(stopRoute, routes, on="route_id", how="inner")
    stopRoute = stopRoute[stopRoute["stop_id"] == stopId]
    stopRoute = stopRoute.drop(columns=[ 'stop_code','stop_lat', 'stop_lon',
       'wheelchair_boarding', 'arrival_time', 'departure_time',
       'stop_sequence', ' pickup_type', 'drop_off_type', 
       'service_id', 'shape_id', 'trip_headsign', 'trip_short_name',
       'agency_id', 'route_short_name',  'route_type'])
    
    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={"arrival_time": "arrival_time_reel"})
    result = result.rename(columns={"departure_time": "departure_time_reel"})

    result = result[result["stop_id"] == stopId]
    result = result.drop(columns=["trip_id","stop_id","direction_id","arrival_delay","departure_delay"])
    if "schedule_relationship" in result.columns:
    # Supprimer la colonne "schedule_relationship"
        result = result.drop(columns=["schedule_relationship"])
    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    

    for index, row in result.iterrows():
        result.loc[index, "arrival_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["arrival_time_reel"]
        ))).astimezone(cet_timezone)
        result.loc[index, "departure_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["departure_time_reel"]
        ))).astimezone(cet_timezone)

    try:
        print("Trajet " + str(stopRoute["route_long_name"].iloc[0]))
    except:
        st.warning(f"Aucune données trouvées pour la date {selected_date}")
        return 0
    
    result=result.sort_values(by="arrival_time_reel", ascending=True)
    print(result)

    differenceArret = pd.DataFrame()
    differenceArret['arrival_time_reel'] = pd.to_datetime(result['arrival_time_reel'])
    differenceArret['departure_time_reel'] = pd.to_datetime(result['departure_time_reel'])

    # Calculer la colonne 'difference' représentant la différence de temps entre deux arrêts successifs
    differenceArret['difference'] = differenceArret['arrival_time_reel'].diff()

    # Remplir la première valeur de 'difference' avec NaT (Not a Time) car il n'y a pas de différence pour la première ligne

    differenceArret = differenceArret.loc[differenceArret['difference'] != pd.Timedelta('00:00:00')]
    differenceArret = differenceArret.dropna(subset=['difference'])

    differenceArret["arrival_hour"] = differenceArret["arrival_time_reel"].dt.hour
    differenceArret=differenceArret.drop(columns=['arrival_time_reel','departure_time_reel'])

    choixCalcul = st.sidebar.selectbox(
        "Méthode de calcul",
        [
            "Temps d'attente moyen",
            "Temps d'attente maximal",
        ],
    )
    agg_funcs={}
    if choixCalcul == "Temps d'attente moyen":
        agg_funcs = {
            "difference": "mean",
        }
    elif choixCalcul == "Temps d'attente maximal":
        agg_funcs = {
            "difference": "max",
        }

    differenceArret = differenceArret.groupby("arrival_hour").agg(agg_funcs).reset_index()
    print(differenceArret)

    differenceArret["difference"] = differenceArret["difference"].dt.total_seconds() / 60
    print(differenceArret)

    # affichage titre histogramme
    st.markdown(
        f"<h5 style='text-align: center;'>Histogramme du {str(choixCalcul)} entre deux bus/tramway sur la Ligne "
        f"{str(stopRoute['route_long_name'].iloc[0])} à l'arrêt "
        f"{str(stopRoute['stop_name'].iloc[0])}</h5>",
        unsafe_allow_html=True,
    )

    # Créer les histogrammes avec Matplotlib
    fig, ax = plt.subplots()
    # création un histogramme des minutes depuis minuit
    ax.bar(
        differenceArret["arrival_hour"],
        differenceArret["difference"],
        align="center",
        label="Durrée d'attente entre deux bus/tramways",
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
    ax.set_ylabel("Durée d'attente (minutes)")

    # affichage du graphique dans Streamlit
    st.pyplot(fig)
    return 0

def busTramSimultane(data_in, selected_date):
    print(
        "\nAffichage histogramme représentant le nombre de trajets par tranche horaire :"
    )
    result=data_in
    
    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={"arrival_time": "arrival_time_reel"})
    result = result.rename(columns={"departure_time": "departure_time_reel"})

    result = result.drop(columns=["stop_id","direction_id","arrival_delay","departure_delay","arrival_time_reel"])
    if "schedule_relationship" in result.columns:
    # Supprimer la colonne "schedule_relationship"
        result = result.drop(columns=["schedule_relationship"])
    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    

    for index, row in result.iterrows():
        result.loc[index, "departure_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["departure_time_reel"]
        ))).astimezone(cet_timezone)
    result['departure_time_reel'] = pd.to_datetime(result['departure_time_reel'])
    result["arrival_hour"] = result["departure_time_reel"].dt.hour
    result=result.drop(columns=["departure_time_reel"])
    result=result.drop_duplicates(subset=["trip_id","arrival_hour"])
    print(result)

    

    

    # affichage titre histogramme
    st.markdown(
        f"<h5 style='text-align: center;'>Histogramme trajets par plages horaires</h5>",
        unsafe_allow_html=True,
    )

    # Créer les histogrammes avec Matplotlib
    fig, ax = plt.subplots()
    # création un histogramme des minutes depuis minuit
    ax.hist(
        result["arrival_hour"],
        bins=range(0, 27),
        alpha=0.5,
        rwidth=0.9,
        align="left",
        label="Trajets par plages horaires",
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
    ax.set_ylabel("Nombre trajets")

    # affichage du graphique dans Streamlit
    st.pyplot(fig)
    return 0

def ficheHoraire(stopId: str, data_in, selected_date):
    print(
        "\nAffichage fiche horaire à un arrêt en particulier :"
    )
    result=data_in
    
    # rename colonne pour ne pas avoir de collisions avec les colonnes d'heures prévues
    result = result.rename(columns={"arrival_time": "arrival_time_reel"})
    result = result.rename(columns={"departure_time": "departure_time_reel"})

    result = result[result["stop_id"].astype(str) == str(stopId)]

    result = result.drop(columns=["stop_id","direction_id","arrival_delay","departure_delay","arrival_time_reel"])
    if "schedule_relationship" in result.columns:
    # Supprimer la colonne "schedule_relationship"
        result = result.drop(columns=["schedule_relationship"])
    # Ajout des colonnes "arrival_time" et "departure_time", afin de comparer les horaires réélles et prévues
    

    for index, row in result.iterrows():
        result.loc[index, "departure_time_reel"] = (original_timezone.localize(datetime.fromtimestamp(
            row["departure_time_reel"]
        ))).astimezone(cet_timezone)
    result['departure_time_reel'] = pd.to_datetime(result['departure_time_reel'])
    result=result.drop_duplicates(subset=["trip_id"])
    result = result.drop(columns=["trip_id"])
    print(result)
    st.markdown(
        f"<h5 style='text-align: center;'>Fiche horaire du {selected_date}</h5>",
        unsafe_allow_html=True,
    )
    st.dataframe(result)
    return 0

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fin fonctions, passage section Menu
# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# Menu pour choisir la fonction à utiliser
if __name__ == "__main__":
    st.sidebar.title("Menu")

    trips = pd.read_csv(f"{nom_GTFS}//trips.txt", delimiter=",")
    
    stopRoute = pd.merge(stops, stop_times, on="stop_id", how="inner")
    stopRoute = pd.merge(stopRoute, trips, on="trip_id", how="inner")
    stopRoute = pd.merge(stopRoute, routes, on="route_id", how="inner")
    stopRoute = stopRoute.drop(columns=[ 'stop_code','stop_lat', 'stop_lon',
       'wheelchair_boarding', 'arrival_time', 'departure_time',
       'stop_sequence', ' pickup_type', 'drop_off_type', 
       'service_id', 'shape_id', 'trip_headsign', 'trip_short_name',
       'agency_id', 'route_short_name', 'trip_id'])
    stopRoute=stopRoute.drop_duplicates(subset="stop_id")
    print(stopRoute.columns)
    print(stopRoute)
    # Ajoute un sélecteur pour choisir la fonctionnalité
    fonctionnalite = st.sidebar.selectbox(
        "Sélectionne une fonctionnalité",
        [
            "Accueil",
            "Ligne avec moyenne de départ en avance",
            "Graphique Arrêts par route",
            "Graphique Arrêts par Stop",
            "Temps d'attente",
            "Nombre trajets par tranche horaire",
            "Fiche Horaire par arrêt",
        ],
    )

    # date picker
    selected_date = st.sidebar.date_input(
        "Sélectionner une date", (datetime.now().date() - timedelta(days=1))
    )
    date_str = selected_date.strftime("%Y_%m_%d")
    nom_dataframe = f"datas_{date_str}"

    if fonctionnalite == "Accueil":
        st.header("Accueil")
    # Appelle la fonction appropriée en fonction de la sélection
    elif fonctionnalite == "Ligne avec moyenne de départ en avance":
        if nom_dataframe in globals():
            departEnAvance(routeParTripParJour(globals()[nom_dataframe]))
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")
    elif fonctionnalite == "Graphique Arrêts par route":
        if nom_dataframe in globals():
            # ligne de trajet picker
            choix_routes = pd.read_csv(f"{nom_GTFS}/routes.txt", delimiter=",")
            ligne_trajet = st.sidebar.selectbox(
                "Sélectionne une Ligne Divia", choix_routes["route_long_name"]
            )
            index = choix_routes[choix_routes["route_long_name"] == ligne_trajet].index[
                0
            ]
            selected_id = choix_routes.loc[index, "route_id"]

            graphJourneeByRoute(selected_id, 0, globals()[nom_dataframe], selected_date)
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")
    elif fonctionnalite == "Graphique Arrêts par Stop":
        if nom_dataframe in globals():
            # stop (arrêt) picker
            choix_stop = pd.read_csv(f"{nom_GTFS}/stops.txt", delimiter=",")
            ligne_trajet = st.sidebar.selectbox(
                "Sélectionne une Ligne Divia", [f"{route_name} - {route_id.replace('4-', '')}" for route_name, route_id in zip(stopRoute['route_long_name'].unique(), stopRoute['route_id'].unique())]
            )
            ligne_trajet = ligne_trajet.split('-')[0].strip()
            index = stopRoute[stopRoute["route_long_name"] == ligne_trajet].index[
                0
            ]
            selected_id = stopRoute.loc[index, "route_id"]

            
            newStopRoute = stopRoute[stopRoute["route_id"] == selected_id]
            stop_choix = st.sidebar.selectbox(
                "Sélectionne un arrêt Divia", newStopRoute['stop_name']
            )
            print(stop_choix)
            index = choix_stop[choix_stop["stop_name"] == stop_choix].index[0]
            selected_id = choix_stop.loc[index, "stop_id"]

            graphJourneeByRouteAndStop(
                selected_id, globals()[nom_dataframe], selected_date
            )
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")
    elif fonctionnalite == "Temps d'attente":
        if nom_dataframe in globals():
            # stop (arrêt) picker
            choix_stop = pd.read_csv(f"{nom_GTFS}/stops.txt", delimiter=",")
            
            ligne_trajet = st.sidebar.selectbox(
                "Sélectionne un arrêt Divia", [f"{stop_id} - {stop_name} - {route_id.replace('4-', '')}" for stop_id, stop_name, route_id in zip(stopRoute['stop_name'], stopRoute['route_long_name'], stopRoute['route_id'])]
            )
            ligne_trajet = ligne_trajet.split('-')[0].strip()
            index = stopRoute[stopRoute["stop_name"] == ligne_trajet].index[0]
            selected_id = stopRoute.loc[index, "stop_id"]

            tpsAttente(
                selected_id, globals()[nom_dataframe], selected_date
            )
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")
    elif fonctionnalite == "Nombre trajets par tranche horaire":
        if nom_dataframe in globals():
            busTramSimultane(globals()[nom_dataframe], selected_date)
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")
    elif fonctionnalite == "Fiche Horaire par arrêt":
        if nom_dataframe in globals():
            # stop (arrêt) picker
            choix_stop = pd.read_csv(f"{nom_GTFS}/stops.txt", delimiter=",")
            ligne_trajet = st.sidebar.selectbox(
                "Sélectionne une Ligne Divia", [f"{route_name} - {route_id.replace('4-', '')}" for route_name, route_id in zip(stopRoute['route_long_name'].unique(), stopRoute['route_id'].unique())]
            )
            ligne_trajet = ligne_trajet.split('-')[0].strip()
            index = stopRoute[stopRoute["route_long_name"] == ligne_trajet].index[
                0
            ]
            selected_id = stopRoute.loc[index, "route_id"]

            
            newStopRoute = stopRoute[stopRoute["route_id"] == selected_id]
            stop_choix = st.sidebar.selectbox(
                "Sélectionne un arrêt Divia", newStopRoute['stop_name']
            )
            print(stop_choix)
            index = choix_stop[choix_stop["stop_name"] == stop_choix].index[0]
            selected_id = choix_stop.loc[index, "stop_id"]

            ficheHoraire(
                selected_id, globals()[nom_dataframe], selected_date
            )
        else:
            st.warning(f"Aucun DataFrame trouvé pour la date {selected_date}")