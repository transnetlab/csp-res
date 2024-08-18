# extract the master variables from the .sol file and store it in a csv file for 1,3,12,52 scenarios
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle

network = 'Canberra_3.91k'
folder_path = f'E:/PycharmProjects/CSP-Benders'
temperature = True
renewables = True
if temperature & renewables:
    list_scenarios = [52, 12, 3, 1]
else:
    list_scenarios = [52]

# open the file
with open('./dict_network_name.pkl', 'rb') as f:
    dict_network_name = pickle.load(f)


data_master_scenarios = pd.DataFrame(
    columns=['scenario', 'location', 'grid_capacity', 'battery_capacity', 'panel_area'])
# read the .sol file and extract the row and column
for index, scenarios in enumerate(list_scenarios):
    if temperature:
        data = pd.read_csv(f'{folder_path}/{network}/{scenarios}_scenario/'
                           f'csp_{dict_network_name[network]}_{scenarios}_benders_True_'
                           f'temperature_True_renewables_{renewables}.sol', delimiter='=')
    else:
        data = pd.read_csv(f'{folder_path}/{network}/without_temperature/1_scenario/csp_'
                           f'{dict_network_name[network]}_{scenarios}_'
                           f'scenarios_benders_True_temperature_{temperature}_renewables_{renewables}.sol',
                           delimiter="=")
    # add new column names without removing the existing ones
    data.columns = ['type', 'variable', 'index', 'slack']
    data = data[:-5]
    # data column names
    data.columns = ['type', 'variable', 'index', 'slack']

    # remove the last 6 letters from each row in name column
    data['variable'] = data['variable'].str[:-6]

    # if type starts with '<constraint' then in row_status dataframe
    # data_constraint = data[data['type'].str.contains('<constraint name')]

    # if type starts with '<variable' then in column_status dataframe
    data_variable = data[data['type'].str.contains('<variable name')]

    # data containing the master variables starting with z or s or a
    data_master = data_variable[data_variable['variable'].str.contains("z|s|a")]

    data_master['value'] = data_master['slack'].str[:-2].copy()
    # convert str to float in value column
    data_master['value'] = data_master['value'].astype(float)
    data_master['variable_type'] = data_master['variable'].str.split("_").str[0]
    data_master['location'] = data_master['variable'].str.split("_").str[1]
    locations = data_master['location'].unique()
    if renewables:
        # map 'z' to grid capacity, 's' to battery capacity and 'a' to panel area
        data_master['variable_type'] = data_master['variable_type'].map({'z': 'grid_capacity', 's': 'battery_capacity',
                                                                         'a': 'panel_area'})
        # for given scenarios, populate the master variables in the dataframe data_master_scenarios
        for location in locations:
            data_master_scenarios = data_master_scenarios._append(
                {'scenario': scenarios, 'location': location,
                 'grid_capacity': data_master[(data_master['location'] == location) &
                                              (data_master['variable_type'] == 'grid_capacity')]['value'].values[0],
                 'battery_capacity': data_master[(data_master['location'] == location) &
                                                 (data_master['variable_type'] == 'battery_capacity')]['value'].values[0],
                 'panel_area': data_master[(data_master['location'] == location) &
                                           (data_master['variable_type'] == 'panel_area')]['value'].values[0]},
                ignore_index=True)

    else:
        # map 'z' to grid capacity, 's' to battery capacity and 'a' to panel area
        data_master['variable_type'] = data_master['variable_type'].map({'z': 'grid_capacity'})
        # for given scenarios, populate the master variables in the dataframe data_master_scenarios
        for location in locations:
            data_master_scenarios = data_master_scenarios._append(
                {'scenario': scenarios, 'location': location,
                 'grid_capacity': data_master[(data_master['location'] == location) &
                                              (data_master['variable_type'] == 'grid_capacity')]['value'].values[0]},
                ignore_index=True)

# check the total number of locations in the network
locations = data_master_scenarios['location'].unique()

# map location from
dict_location_mapping = {}
mapping_number = 1
for location in locations:
    dict_location_mapping[str(location)] = mapping_number
    mapping_number += 1

# save the dict_location_mapping in a pickle file
with open(f'{folder_path}/{network}/dict_location_mapping_visualization.pkl', 'wb') as f:
    pickle.dump(dict_location_mapping, f)

for scenarios in list_scenarios:
    # check if the location is not present in the dataframe for given scenarios, add the location with 0 values
    set_of_locations = set(data_master_scenarios[data_master_scenarios['scenario'] == scenarios]['location'])
    not_present_locations = set(locations) - set_of_locations
    for location in not_present_locations:
        data_master_scenarios = data_master_scenarios._append(
            {'scenario': scenarios, 'location': location, 'grid_capacity': 0, 'battery_capacity': 0, 'panel_area': 0},
            ignore_index=True)

dict_location = {}
# round off the values to 2 decimal places
data_master_scenarios = data_master_scenarios.round(2)
color_dict = {
    1: '#66CCCC',  # Lighter Teal
    3: '#FFE680',  # Lighter Gold
    12: '#FF6F7A', # Lighter Crimson
    52: '#7A94E6'  # Lighter Royal Blue
}


# hatch_dict = {
#     1: 'x',
#     3: '+',
#     12: 'o',
#     52: ''
# }
dict_units = {'grid_capacity': 'Grid Capacity (kW)', 'battery_capacity': 'Battery Capacity (kWh)', 'panel_area': 'Panel Area (m$^2$)'}
# for grid capacity
list_master = ['grid_capacity', 'battery_capacity', 'panel_area']
# remove the location for which all scenarios have 0 values
for master in list_master:
    dict_location[master] = []
    for location in locations:
        location = str(location)
        count = 0
        for scenarios in list_scenarios:
            try:
                if data_master_scenarios[(data_master_scenarios['scenario'] == scenarios) &
                                         (data_master_scenarios['location'] == location)][master].values[0] != 0:
                    break
                else:
                    count += 1
            except IndexError:
                count += 1
        if count == len(list_scenarios):
            # remove that location
            dict_location[master].append(location)

dict_fig_size = {'grid_capacity': (12, 6), 'battery_capacity': (24, 12), 'panel_area': (24, 12)}
dict_bar_width = {'grid_capacity': 0.2, 'battery_capacity': 0.22, 'panel_area': 0.22}
dict_font_size = {'grid_capacity': 16, 'battery_capacity': 32, 'panel_area': 32}
dict_label_size = {'grid_capacity': 20, 'battery_capacity': 40, 'panel_area': 40}


for master in list_master:
    # Set up the figure and axis
    fig, ax = plt.subplots(1, figsize=dict_fig_size[master])
    bar_width = dict_bar_width[master]
    # take those locations which are present in dict_location
    data_master_scenarios_ = data_master_scenarios[~data_master_scenarios['location'].isin(dict_location[master])]
    indices = np.arange(len(data_master_scenarios_['location'].unique()))
    # map location from dict_location_mapping
    data_master_scenarios_['location'] = data_master_scenarios_['location'].map(dict_location_mapping)

    # sort the data based on location
    data_master_scenarios_ = data_master_scenarios_.sort_values(by='location')
    locations = data_master_scenarios_['location'].unique()
    for i, j in enumerate(list_scenarios):

        data = data_master_scenarios_[data_master_scenarios_['scenario'] == j][master]

        ax.bar(indices + i * bar_width, data, bar_width, label=f'{j} scenario', color=color_dict[j],
                edgecolor='#323232')
    ax.set_xticks(indices + (bar_width * 2))
    ax.set_xticklabels([location for location in locations])
    # set x_ticks font size
    plt.xticks(fontsize=dict_font_size[master])
    # set y_ticks font size
    plt.yticks(fontsize=dict_font_size[master])
    # Set labels and title
    ax.set_xlabel('Charging Location', fontsize=dict_label_size[master])
    ax.set_ylabel(dict_units[master], fontsize=dict_label_size[master])
    # ax.set_title('Bar Graph with 4 Scenarios for Each Variable')
    # Display the legend
    ax.legend()
    # increase the font size of legend
    plt.legend(fontsize=dict_font_size[master])
    # save the plot
    plt.savefig(f'{folder_path}/{network}/visualization/master_variables_{master}_{network}.pdf', bbox_inches='tight')
    # Show the plot
    plt.show()

# Total contracted grid cost
Unit_battery_price = np.asarray([0.046], dtype=np.float64)
Unit_capacity_cost = np.asarray([0.14], dtype=np.float64)
Unit_panel_cost = np.asarray([0.017], dtype=np.float64)
for scenarios in list_scenarios:
    total_grid_cost = data_master_scenarios[data_master_scenarios['scenario'] == scenarios]['grid_capacity'].sum() * Unit_capacity_cost[0]
    total_battery_cost = data_master_scenarios[data_master_scenarios['scenario'] == scenarios]['battery_capacity'].sum() * Unit_battery_price[0]
    total_panel_cost = data_master_scenarios[data_master_scenarios['scenario'] == scenarios]['panel_area'].sum() * Unit_panel_cost[0]
    print(f"Total grid cost for {scenarios} scenarios: {total_grid_cost*1.09}")
    print(f"Total panel cost for {scenarios} scenarios: {total_panel_cost*1.09}")
    print(f"Total battery cost for {scenarios} scenarios: {total_battery_cost *1.09}")

