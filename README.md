# GitHub-Divia-PFE-Augusti-Develay
 Répertoire GitHub du Projet de fin d'étude sur l'analyse de données du réseau Divia à Dijon.

## GTFS Description des fichiers
### agency.txt
`agency_id`, `agency_name`, `agency_url`, `agency_timezone`
Description de l'agence

### calendar_dates.txt
`service_id`, `date`, `exception_type`
Liste de tous les services avec la date associée, fichier en lien avec calendar.txt et trips.txt

### calendar.txt
`service_id`, `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`, `start_date`, `end_date`
Détail du calendrier en fonction du `service_id` associé à calendar.txt

### routes.txt
`route_id`, `agency_id`, `route_short_name`, `route_long_name`, `route_type`
Détail des routes associés à `route_id` lié au fichier  trips.txt

### shapes.txt
Différents points géographiques permettant de créer le réseau sur une carte

### stop_times.txt
`trip_id`, `arrival_time`, `departure_time`, `stop_id`, `stop_sequence`, `pickup_type`, `drop_off_type`
Données statiques sur les prévisions des horaires de chaques trips, associés à `trip_id` lié au fichier trips.txt

### trips.txt
`route_id`, `service_id`, `shape_id`, `trip_id`, `trip_headsign`, `trip_short_name`, `direction_id`
Fichier permettant de lier plusieurs fichiers (calendar_dates.txt, stop_times.txt, calendar.txt), rendant le tout comme une base de données. Et, donnant des informations précises sur un trip en particulier (`direction_id` : sens de circulation)