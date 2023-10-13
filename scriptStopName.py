import pandas as pd

data=pd.read_csv('GTFS/stop_name.txt',delimiter=',')
print(data.head(10))
data['stop_id'] = '4-' + data['stop_id'].astype(str)
data.to_csv('votre_fichier.txt', index=False,sep=',')

print("Le fichier a été mis à jour avec les nouvelles données.")