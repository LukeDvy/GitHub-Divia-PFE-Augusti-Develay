import pandas as pd

#Chargement des fichiers GTFS dans des df
agency=pd.read_csv('GTFS/agency.txt',delimiter=',')
calendar_dates=pd.read_csv('GTFS/calendar_dates.txt',delimiter=',')
calendar=pd.read_csv('GTFS/calendar.txt',delimiter=',')
routes=pd.read_csv('GTFS/routes.txt',delimiter=',')
shapes=pd.read_csv('GTFS/shapes.txt',delimiter=',')
stop_times=pd.read_csv('GTFS/stop_times.txt',delimiter=',')
stops=pd.read_csv('GTFS/stops.txt',delimiter=',')
trips=pd.read_csv('GTFS/trips.txt',delimiter=',')

#print(agency.head(10))

#1ere recherche : pour une date donnée, recherche des trips et quelques détails
date_cherche = '20231207'
date_correct = calendar_dates[calendar_dates['date'].astype(str) == str(date_cherche)]
print(date_correct)
'''route_retenue=pd.DataFrame()
for index, row in date_correct.iterrows(): #lis chaque ligne à la date du 07/12/2023, et pour chaque service_id
    jour=calendar[row['service_id'] == calendar['service_id'].astype(str)]
    route_retenue=trips[row['service_id'] == trips['service_id'].astype(str)]
    
    print("--------------------------------")
    if not route_retenue.empty:
    # Filtrer le DataFrame "routes" en utilisant route_retenue
        routes_detail = routes[routes['route_id'].astype(str) == route_retenue['route_id'].astype(str).values[0]]
        print(routes_detail)
    else:
        print("route_retenue est vide, impossible de filtrer routes_detail")'''

# fusionne les df en utilisant la colonne 'service_id'
new_base = pd.merge(trips, date_correct, on='service_id', how='inner')
result = pd.merge(new_base, routes, on='route_id', how='inner')

# séleectionne certaines colonnes souhaitées
columns_to_display = ['route_id', 'route_short_name', 'route_long_name', 'route_type']

# traduction de la colonne route_type de int à string : 0=Tram, 3=Bus
result['route_type'] = result['route_type'].astype(str)
for index, row in result.iterrows():
    if str(row['route_type'])=="3":
        result.loc[index, 'route_type'] = "Bus"
    if str(row['route_type'])=="0":
        result.loc[index, 'route_type'] = "Tramway"
result = result[columns_to_display]

# Afficher les résultats
print(result.drop_duplicates())