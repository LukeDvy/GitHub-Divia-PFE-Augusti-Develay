import pandas as pd

#Chargement des fichiers GTFS dans des df
agency=pd.read_csv('GTFS/agency.txt')
calendar_dates=pd.read_csv('GTFS/calendar_dates.txt')
calendar=pd.read_csv('GTFS/calendar.txt')
routes=pd.read_csv('GTFS/routes.txt')
shapes=pd.read_csv('GTFS/shapes.txt')
stop_times=pd.read_csv('GTFS/stop_times.txt')
stops=pd.read_csv('GTFS/stops.txt')
trips=pd.read_csv('GTFS/trips.txt')

print(agency.head(10))