import requests
from haversine import haversine, Unit
import pandas as pd
import multiprocessing

network = "Newyork"
stops = pd.read_csv(f'./{network}/stops.txt')

min_lat = min(list(stops.stop_lat)) - 0.04
max_lat = max(list(stops.stop_lat)) + 0.04
min_lon = min(list(stops.stop_lon)) - 0.04
max_lon = max(list(stops.stop_lon)) + 0.04

distance_csv = pd.DataFrame(columns=['start_stop', 'end_stop', 'distance'])
distance_dict = {}


def calculate_distance(start_row, end_row):
    start_lat, start_lon = start_row['stop_lat'], start_row['stop_lon']
    end_lat, end_lon = end_row['stop_lat'], end_row['stop_lon']
    try:
        response = requests.get(f"http://127.0.0.1:5000/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?steps=true&geometries=geojson")
        data = response.json()
        distance = data['routes'][0]['distance']  # Distance in meters
        distance_in_km = distance / 1000
        print(distance_in_km)# Convert to kilometers
        return round(distance_in_km, 3)
    except Exception as e:
        try:
            response = requests.get(f"http://127.0.0.1:5000/route/v1/driving/{end_lon},{end_lat};{start_lon},{start_lat}?steps=true&geometries=geojson")
            data = response.json()
            distance = data['routes'][0]['distance']  # Distance in meters
            distance_in_km = distance / 1000
            print(distance_in_km)# Convert to kilometers
            return round(distance_in_km, 3)
        except Exception as e:
            return round(haversine((start_lat, start_lon), (end_lat, end_lon), unit=Unit.KILOMETERS), 3)

def process_chunk(args):
    start_index, chunk = args
    distance_csv = pd.DataFrame(columns=['start_stop', 'end_stop', 'distance'])
    distance_dict = {}
    for index, start_row in chunk.iterrows():
        for index1, end_row in stops.iterrows():
            distance = calculate_distance(start_row, end_row)
            distance_dict[(start_row['stop_id'], end_row['stop_id'])] = distance
            distance_csv.loc[len(distance_csv)] = [start_row['stop_id'], end_row['stop_id'], distance]
    return distance_csv

# Split the stops into chunks for parallel processing
chunk_size = 10
chunks = [(i, stops[i:i+chunk_size]) for i in range(0, len(stops), chunk_size)]

with multiprocessing.Pool(processes=10) as pool:
    results = pool.map(process_chunk, chunks)

distance_csv_ = pd.DataFrame(columns=['start_stop', 'end_stop', 'distance'])
# concatenate the results
for i in range(len(results)):
    distance_csv_ = pd.concat([distance_csv, results[i]])

# save the distance_csv as csv file
distance_csv_.to_csv(f'./{network}/distance_file.csv', index=False)

# save the distance_dict as pickle
# import pickle
# with open(f'./{network}/distance_file.pkl', 'wb') as f:
#     pickle.dump(distance_dict, f)

