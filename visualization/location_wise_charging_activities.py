import matplotlib.pyplot as plt
import pandas as pd
import pickle

network = 'Canberra_3.91k'
scenarios = 52
temperature = True
renewables = True
folder_path = f'E:/PycharmProjects/CSP-Benders'

# open the file dict_network_name.pkl
with open('./dict_network_name.pkl', 'rb') as f:
    dict_network_name = pickle.load(f)

if temperature:
    data = pd.read_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/csp_{dict_network_name[network]}_{scenarios}_benders_True_'
        f'temperature_{temperature}_renewables_{renewables}.sol', delimiter="=")
else:
    data = pd.read_csv(f'{folder_path}/{network}/without_temperature/1_scenario/csp_'
                       f'{dict_network_name[network]}_{scenarios}_'
                       f'scenarios_benders_True_temperature_{temperature}_renewables_{renewables}.sol', delimiter="=")
data = data[24:-5]
# data column names
data.columns = ['type', 'name', 'index', 'slack']

# remove the last 6 letters from each row in name column
data['name'] = data['name'].str[:-6]

# if type starts with '<variable' then in column_status dataframe
data_variable = data[data['type'].str.contains('<variable name')]

# child variables containing both x and y in the name
data_grid_solar = data_variable[data_variable['name'].str.contains("x")]
data_solar = data_variable[data_variable.loc[:, 'name'].str.contains("y")]
data_grid_solar.loc[:, 'value'] = data_grid_solar.loc[:, 'slack'].str[:-2].copy()
data_solar.loc[:, 'value'] = data_solar.loc[:, 'slack'].str[:-2].copy()

# find the location of decision variables
data_grid_solar.loc[:, 'location'] = data_grid_solar.loc[:, 'name'].str.split("_").str[3]
data_solar.loc[:, 'location'] = data_solar.loc[:, 'name'].str.split("_").str[3]

# unique locations
locations = data_grid_solar['location'].unique()

# take one location in the data_grid_solar
data_grid_solar = data_grid_solar[data_grid_solar['location'] == locations[0]]
data_solar = data_solar[data_solar['location'] == locations[0]]

# find the scenario
data_grid_solar.loc[:, 'status'] = data_grid_solar.loc[:, 'name'].str.split("_").str[1]
data_solar.loc[:, 'status'] = data_solar.loc[:, 'name'].str.split("_").str[1]

# convert str to float in value column
data_grid_solar.loc[:, 'value'] = data_grid_solar.loc[:, 'value'].astype(float)
data_solar.loc[:, 'value'] = data_solar.loc[:, 'value'].astype(float)

# find the time_stamp
data_grid_solar.loc[:, 'time_stamp'] = data_grid_solar.loc[:, 'name'].str.split("_").str[4]
data_solar.loc[:, 'time_stamp'] = data_solar.loc[:, 'name'].str.split("_").str[4]

# group by time_stamp and status
data_grid_solar_grouped = data_grid_solar.groupby(['time_stamp', 'status']).agg({'value': 'sum'}).reset_index()
data_solar_grouped = data_solar.groupby(['time_stamp', 'status']).agg({'value': 'sum'}).reset_index()

# # plot a graph
# plt.figure(figsize=(20, 10))
# for i in [10, 26, 50]:
#     data = data_grid_solar_grouped[data_grid_solar_grouped['status'] == str(i)]
#     plt.plot(data['time_stamp'], data['value'], label=f'scenario {i}')
# plt.show()

# plot a graph
import numpy as np

# Sample data

y1 = data_grid_solar_grouped[data_grid_solar_grouped['status'] == str(10)]
y11 = data_solar_grouped[data_solar_grouped['status'] == str(10)]
# convert the time_stamp to int type
y1['time_stamp'] = y1['time_stamp'].astype(int)
y11['time_stamp'] = y11['time_stamp'].astype(int)
y2 = data_grid_solar_grouped[data_grid_solar_grouped['status'] == str(26)]
y22 = data_solar_grouped[data_solar_grouped['status'] == str(26)]
y2['time_stamp'] = y2['time_stamp'].astype(int)
y22['time_stamp'] = y22['time_stamp'].astype(int)
y3 = data_grid_solar_grouped[data_grid_solar_grouped['status'] == str(50)]
y33 = data_solar_grouped[data_solar_grouped['status'] == str(50)]
y3['time_stamp'] = y3['time_stamp'].astype(int)
y33['time_stamp'] = y33['time_stamp'].astype(int)

min_time_stamp = min(min(y1['time_stamp']), min(y2['time_stamp']), min(y3['time_stamp']))
max_time_stamp = max(max(y1['time_stamp']), max(y2['time_stamp']), max(y3['time_stamp']))
x = np.linspace(min_time_stamp, max_time_stamp, max_time_stamp - min_time_stamp + 1)

# add the missing time_stamps and value 0
for i in range(min_time_stamp, max_time_stamp + 1):
    if i not in y1['time_stamp'].values:
        y1 = y1._append({'time_stamp': i, 'status': 10, 'value': 0}, ignore_index=True)
        y11 = y11._append({'time_stamp': i, 'status': 10, 'value': 0}, ignore_index=True)
    if i not in y2['time_stamp'].values:
        y2 = y2._append({'time_stamp': i, 'status': 26, 'value': 0}, ignore_index=True)
        y22 = y22._append({'time_stamp': i, 'status': 26, 'value': 0}, ignore_index=True)
    if i not in y3['time_stamp'].values:
        y3 = y3._append({'time_stamp': i, 'status': 50, 'value': 0}, ignore_index=True)
        y33 = y33._append({'time_stamp': i, 'status': 50, 'value': 0}, ignore_index=True)


# Create subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

# Plot the first set of data
ax1.plot(x, y11['value'] + y1['value'], color='green', label='Solar Powered')
ax1.plot(x, y1['value'], color='red', label='Grid Powered')
ax1.set_title('Week 10', fontsize=10)
# no x ticks
ax1.tick_params(bottom=False)
# set y ticks size
ax1.tick_params(axis='y', labelsize=9)
ax1.legend()


# Plot the second set of data
ax2.plot(x, y22['value'] + y2['value'], color='green')
ax2.plot(x, y2['value'], color='red')
ax2.set_ylabel('Energy (kWh)', fontsize=15)
ax2.tick_params(bottom=False)
ax2.tick_params(axis='y', labelsize=9)
ax2.set_title('Week 26', fontsize=10)

# Plot the third set of data
ax3.plot(x, y33['value'] + y3['value'], color='green')
ax3.plot(x, y3['value'], color='red')
ax3.set_title('Week 50', fontsize=10)
ax3.set_xlabel('Time', fontsize=15)
ax3.tick_params(axis='y', labelsize=9)

xtick_labels = []
# on x ticks show time_stamp in hours format
for time in range(min_time_stamp//60, max_time_stamp//60):
    if time % 24 > 9:
        xtick_labels.append(f'{time % 24}')
    else:
        xtick_labels.append(f'0{time % 24}')

plt.xticks(x[::60], xtick_labels, fontsize=9)

# set ytick range
plt.yticks(np.arange(0, 15, step=10))

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.9)  # Make space for the figure title

# save the .pdf file
plt.savefig(f'{folder_path}/{network}/visualization/'
            f'{network}_energy_powered_{network}_location_'
            f'{locations[0][:-2]}.pdf', bbox_inches='tight')
# Show plot
plt.show()
