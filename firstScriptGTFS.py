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

#1ere recherche : pour une date donnée, recherche des 
date_cherche = '20231207'
date_correct = calendar_dates[calendar_dates['date'].astype(str) == str(date_cherche)]
print(date_correct)

for index, row in date_correct.iterrows():
    jour=calendar[row['service_id'] == calendar['service_id'].astype(str)]
    route_id=trips[row['service_id'] == trips['service_id'].astype(str)]
    if not jour.empty:
        print(jour)
    if not route_id.empty:
        print(route_id)