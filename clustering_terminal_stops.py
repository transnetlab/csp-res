import pandas as pd
import pickle

network = 'Surat'
# open stops file
stops = pd.read_csv(f'./{network}/stops.txt')
stop_times = pd.read_csv(f'./{network}/stop_times.txt')
trips = pd.read_csv(f'./{network}/trips.txt')
# extract the terminal stops
# find the terminal stops
terminal_stops_ = stop_times.groupby('trip_id').agg({'stop_id': ['first', 'last']}).reset_index()
# take unique of start and last stop
terminal_stops = set(terminal_stops_[('stop_id', 'first')].unique()).union(set(terminal_stops_[('stop_id', 'last')].unique()))
# open the distance_file.pkl
with open(f'./{network}/distance_file.pkl', 'rb') as f:
    distance_file_dict = pickle.load(f)
# open distance_file.csv
distance_file = pd.read_csv(f'./{network}/distance_file.csv')
# convert to int type
distance_file['start_stop'] = distance_file['start_stop'].astype(int)
distance_file['end_stop'] = distance_file['end_stop'].astype(int)

distance_file = distance_file[distance_file['start_stop'].isin(terminal_stops) & distance_file['end_stop'].isin(terminal_stops)]

# for trips in stop_times_filtered
dict_terminal_stops = {}
for terminal in terminal_stops:
    dict_terminal_stops[terminal] = [set(), set()]

count = 0
for trip in trips['trip_id']:
    print(count)
    start_stop = stop_times[stop_times['trip_id'] == trip].iloc[0]['stop_id']
    end_stop = stop_times[stop_times['trip_id'] == trip].iloc[-1]['stop_id']
    dict_terminal_stops[start_stop][0].add(trip)
    dict_terminal_stops[end_stop][1].add(trip)
    count += 1

# find the frequency of trips passing through each terminal stops
dict_terminal_frequency_start = {}
dict_terminal_frequency_end = {}
df = pd.DataFrame(columns=['Terminal Stop', 'Frequency_Start', 'Frequency_End'])
for terminal in terminal_stops:
    dict_terminal_frequency_start[terminal] = len(dict_terminal_stops[terminal][0])
    dict_terminal_frequency_end[terminal] = len(dict_terminal_stops[terminal][1])
    df = df._append({'Terminal Stop': terminal, 'Frequency_Start': len(dict_terminal_stops[terminal][0])
                   ,'Frequency_End': len(dict_terminal_stops[terminal][1])}, ignore_index=True)

df['Total_Frequency'] = df['Frequency_Start'] + df['Frequency_End']

# find the cluster of terminal stops
dict_cluster = {}

for terminal in terminal_stops:
    data_cluster = distance_file[distance_file['start_stop'] == terminal]
    # find the stops which are within 500m or 0.5km
    cluster = set(data_cluster[data_cluster['distance'] <= 0.5]['end_stop'])
    dict_cluster[terminal] = cluster

# print the cluster with more than 3 terminal stops
for key, value in dict_cluster.items():
    if len(value) >= 3:
        print(key, value)

unique_sets = set()
for key, value in dict_cluster.items():
    if len(value) >= 2:
        unique_sets.add(frozenset(value))


dict_terminal = {}
total_stops_count = 0
for pair in unique_sets:
    data_pair = df[df['Terminal Stop'].isin(pair)]
    # find the stop with the highest frequency
    stop = data_pair[data_pair['Total_Frequency'] == data_pair['Total_Frequency'].max()]['Terminal Stop'].values[0]
    dict_terminal[stop] = pair
    total_stops_count += len(pair)

# find the stops which are subset of other clusters
dict_terminal_subset = {}
for key, value in dict_terminal.items():
    for key1, value1 in dict_terminal.items():
        if value.issubset(value1) and key != key1:
            dict_terminal_subset[key] = value

# remove the subset from the dict_terminal
for key, value in dict_terminal_subset.items():
    del dict_terminal[key]

# find the total stops in the clusters
total_stops_count = 0
for key, value in dict_terminal.items():
    total_stops_count += len(value)

print('total terminal stops:', (len(terminal_stops) + len(dict_terminal) - total_stops_count))

dict_terminal_mapping = {}
for key, value in dict_terminal.items():
    for val in value:
        dict_terminal_mapping[val] = key

stops_not_in_terminal = terminal_stops - set(dict_terminal_mapping.keys())

for stop in stops_not_in_terminal:
    dict_terminal_mapping[stop] = stop

# save the dict_terminal_mapping
with open(f'./{network}/dict_terminal_mapping.pkl', 'wb') as f:
    pickle.dump(dict_terminal_mapping, f)

