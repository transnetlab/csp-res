# import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# fetch the current directory
# CURR_DIR = os.path.dirname(os.path.realpath(__file__))


# print(CURR_DIR)

def analyze_benders_results(network, folder_path):
    """
    Analyzes and plots energy required for each scenario in a network.
    :param network: Network name
    :param folder_path: Folder path to the network
    :return:
    """
    # network = 'Durham_2.1k'
    scenarios = 52
    temperature = True
    renewables = True
    # folder_path = CURR_DIR[:-22]
    # print(folder_path)

    # open the file dict_network_name.pkl
    with open(f'{folder_path}/dict_network_name.pkl', 'rb') as f:
        dict_network_name = pickle.load(f)

    # read the .sol file
    if temperature:
        data = pd.read_csv(
            f'{folder_path}/{network}/{scenarios}_scenario/csp_{dict_network_name[network]}_{scenarios}_benders_True_'
            f'temperature_{temperature}_renewables_{renewables}.sol', delimiter="=")
    else:
        data = pd.read_csv(f'{folder_path}/{network}/without_temperature/1_scenario/csp_'
                           f'{dict_network_name[network]}_{scenarios}_'
                           f'scenarios_benders_True_temperature_{temperature}_renewables_{renewables}.sol',
                           delimiter="=")

    data = data[24:-5]

    # data column names
    data.columns = ['type', 'variable name', 'variable index', 'value']

    # remove the last 6 letters from each row in name column
    data['variable name'] = data['variable name'].str[:-6]

    # if type starts with '<variable' then in column_status dataframe
    data_variable = data[data['type'].str.contains('<variable name')]

    # print(data)
    # print(data_variable)
    # keep only the variable name, index and value columns in data_variable
    data_variable = data_variable[['variable name', 'variable index', 'value']]
    # from the variable index column remove "value" from every entry and convert the type into integer
    data_variable['variable index'] = data_variable['variable index'].str[:-6].astype(int)
    # remove /> from the value column and convert the type into float
    data_variable['value'] = data_variable['value'].str[:-2].astype(float)
    # round the value column to 3 decimal places
    # data_variable['value'] = data_variable['value'].round(3)
    # save data_variable in a csv file

    data_variable.to_csv(f'{folder_path}/{network}/{scenarios}_scenario/data_variable.csv', index=False, header=True)
    # find the maximum and minimum values of variables whose name starts with "z_"
    # open the file

    # sum all the variables whose name starts with "h_10" and have a value greater than 1e-06
    sum_h = data_variable[data_variable['variable name'].str.contains('h_10') & (data_variable['value'] != 0)][
        'value'].sum()
    sum_y = data_variable[data_variable['variable name'].str.contains('y_10') & (data_variable['value'] != 0)][
        'value'].sum()
    print(f"Sum of h variables = {sum_h}")
    print(f"Sum of y variables = {sum_y}")

    data_variable = pd.read_csv(f'{folder_path}/{network}/{scenarios}_scenario/data_variable.csv')
    data_master_grid = data_variable[data_variable['variable name'].str.contains('z_')]
    data_master_panel = data_variable[data_variable['variable name'].str.contains('a_')]
    data_master_battery = data_variable[data_variable['variable name'].str.contains('s_')]
    # find the maximum and minimum values of master variables
    max_grid = data_master_grid['value'].max()
    min_grid = data_master_grid['value'].min()
    max_panel = data_master_panel['value'].max()
    min_panel = data_master_panel['value'].min()
    max_battery = data_master_battery['value'].max()
    min_battery = data_master_battery['value'].min()
    print(f"Maximum grid capacity = {max_grid} &  Minimum grid capacity = {min_grid}")
    print(f"Maximum solar panel area = {max_panel} &  Minimum solar panel area = {min_panel}")
    print(f"Maximum BESS capacity = {max_battery} &  Minimum BESS capacity = {min_battery}")
    # filter x, y, h, v variables and find the maximum and minimum values
    data_scenario_grid_bus = data_variable[data_variable['variable name'].str.contains('x_')]
    data_scenario_solar_battery = data_variable[data_variable['variable name'].str.contains('y_')]
    data_scenario_grid_battery = data_variable[data_variable['variable name'].str.contains('h_')]
    data_scenario_battery_level = data_variable[data_variable['variable name'].str.contains('v_')]
    # find the maximum and minimum values of scenario variables
    max_grid_bus = data_scenario_grid_bus['value'].max()
    min_grid_bus = data_scenario_grid_bus['value'].min()
    max_solar_battery = data_scenario_solar_battery['value'].max()
    min_solar_battery = data_scenario_solar_battery['value'].min()
    max_grid_battery = data_scenario_grid_battery['value'].max()
    min_grid_battery = data_scenario_grid_battery['value'].min()
    max_battery_level = data_scenario_battery_level['value'].max()
    min_battery_level = data_scenario_battery_level['value'].min()
    print(max_grid_bus, min_grid_bus)
    print(max_solar_battery, min_solar_battery)
    print(f"Maximum grid to battery = {max_grid_battery} & Minimum grid to battery = {min_grid_battery}")
    print(max_battery_level, min_battery_level)
    # filter the variables starting with "d_" and "u_"
    data_grid_d = data_variable[data_variable['variable name'].str.contains('d_')]
    data_bus_level = data_variable[data_variable['variable name'].str.contains('u_')]
    # find the maximum and minimum values of d and u variables
    max_grid_d = data_grid_d['value'].max()
    min_grid_d = data_grid_d['value'].min()
    max_bus_level = data_bus_level['value'].max()
    min_bus_level = data_bus_level['value'].min()
    print(max_grid_d, min_grid_d)
    print(max_bus_level, min_bus_level)

    # for any j, collect all the v values and corresponding timestamps in two lists
    data_scenario_battery_level = data_variable[data_variable['variable name'].str.contains('v_')]
    # v variables have the first index as scenario, second index as location, third index as time_stamp
    # filter first scenario values based on "v_{}_{}_{}" format
    data_scenario_1 = data_scenario_battery_level[data_scenario_battery_level['variable name'].str.contains('v_1_')]
    print(data_scenario_1)
    # find all the unique locations
    locations = data_scenario_1['variable name'].str.split("_").str[2].unique()
    print(locations)
    # find the location index corresponding the maximum battery level
    max_battery_level_loc = data_scenario_1.loc[data_scenario_1['value'].idxmax()]['variable name'].split("_")[2]
    print(f"Max battery level loc = {max_battery_level_loc}")
    # filter the data based on the first location
    data_scenario_1_loc = data_scenario_1[data_scenario_1['variable name'].str.contains('v_1_' + locations[12])]
    print(data_scenario_1_loc)
    # find the maximum and minimum values of battery level for the first scenario and first location
    max_battery_level = data_scenario_1_loc['value'].max()
    min_battery_level = data_scenario_1_loc['value'].min()
    print(max_battery_level, min_battery_level)
    # collect all the timestamps and corresponding battery levels in two lists
    timestamps = data_scenario_1_loc['variable name'].str.split("_").str[3]
    battery_levels = data_scenario_1_loc['value']
    print(timestamps)
    print(battery_levels)
    # map the timestamps and battery levels in a dictionary and sort the dictionary based on timestamps in ascending order
    dict_timestamps_battery_levels = dict(zip(timestamps, battery_levels))
    dict_timestamps_battery_levels = dict(sorted(dict_timestamps_battery_levels.items()))
    print(dict_timestamps_battery_levels)
    # plot timestamps vs battery levels using line plot
    # plt.plot(list(dict_timestamps_battery_levels.keys()), list(dict_timestamps_battery_levels.values()))
    # if there is a decrease color the segment by red and if there is an increase color the segment by green,
    # else keep it as blue
    plt.figure(figsize=(12, 6))

    for i in range(len(list(dict_timestamps_battery_levels.keys())) - 1):
        if list(dict_timestamps_battery_levels.values())[i] > list(dict_timestamps_battery_levels.values())[i + 1]:
            plt.plot(
                [list(dict_timestamps_battery_levels.keys())[i], list(dict_timestamps_battery_levels.keys())[i + 1]],
                [list(dict_timestamps_battery_levels.values())[i],
                 list(dict_timestamps_battery_levels.values())[i + 1]],
                color='red')
        elif list(dict_timestamps_battery_levels.values())[i] < list(dict_timestamps_battery_levels.values())[i + 1]:
            plt.plot(
                [list(dict_timestamps_battery_levels.keys())[i], list(dict_timestamps_battery_levels.keys())[i + 1]],
                [list(dict_timestamps_battery_levels.values())[i],
                 list(dict_timestamps_battery_levels.values())[i + 1]],
                color='green')
        else:
            plt.plot(
                [list(dict_timestamps_battery_levels.keys())[i], list(dict_timestamps_battery_levels.keys())[i + 1]],
                [list(dict_timestamps_battery_levels.values())[i],
                 list(dict_timestamps_battery_levels.values())[i + 1]],
                color='blue')

    xtick_labels = []
    min_time_stamp = int(min(dict_timestamps_battery_levels.keys()))
    max_time_stamp = int(max(dict_timestamps_battery_levels.keys()))
    x = np.linspace(0, max_time_stamp - min_time_stamp, max_time_stamp - min_time_stamp + 1)
    # on x ticks show time_stamp in hours format
    if network == 'Canberra_3.91k':
        for time in range(min_time_stamp // 60, max_time_stamp // 60):
            # add + 1 for the Durham network and remove the + 1 to run Canberra network in the for loop
            if time % 24 > 9:
                xtick_labels.append(f'{time % 24}')
            else:
                xtick_labels.append(f'0{time % 24}')
    else:
        for time in range(min_time_stamp // 60, max_time_stamp // 60 + 1):
            # add + 1 for the Durham network and remove the + 1 to run Canberra network in the for loop
            if time % 24 > 9:
                xtick_labels.append(f'{time % 24}')
            else:
                xtick_labels.append(f'0{time % 24}')

    # pick the alternate entries from xtick_labels
    xtick_labels = xtick_labels[::2]
    if network == 'Canberra_3.91k':
        xtick_labels.append('23')
    # print(xtick_labels)
    # print(x[::120])
    # print(x[::120])
    # print(len(xtick_labels))
    # print(len(x[::120]))

    plt.xticks(x[::120], xtick_labels, fontsize=16)
    plt.yticks(fontsize=16)

    plt.xlabel('Hour', fontsize=20)
    plt.ylabel('Battery Level (kWh)', fontsize=20)
    # plt.title('BESS Energy Level vs. Time')
    # plt.show()
    # plt.savefig(f'{folder_path}/{network}/{scenarios}_scenario/bess_battery_level_vs_time_{network}.pdf', dpi=300,
    #             bbox_inches='tight')

    # filter u variables based on the first scenario and plot bus energy level vs time
    data_bus_level = data_variable[data_variable['variable name'].str.contains('u_1_')]
    # find all the unique buses
    buses = data_bus_level['variable name'].str.split("_").str[2].unique()
    print(buses)
    # filter the first bus
    data_bus_1 = data_bus_level[data_bus_level['variable name'].str.contains('u_1_' + buses[0])]
    print(data_bus_1)
    # filter all the "x_1_1_" variables and "y_1_1_" variables
    data_grid_bus = data_variable[data_variable['variable name'].str.contains('x_1_1_')]
    data_solar_bus = data_variable[data_variable['variable name'].str.contains('y_1_1_')]
    print(data_grid_bus)
    print(data_solar_bus)
    # do a timestamp and variable index mapping for data_grid_bus and data_solar_bus in a dictionary
    dict_timestamps_grid = dict(zip(data_grid_bus['variable name'].str.split("_").str[4].astype(int),
                                    data_grid_bus['variable index']))
    dict_timestamps_solar = dict(zip(data_solar_bus['variable name'].str.split("_").str[4].astype(int),
                                     data_solar_bus['variable index']))
    print(dict_timestamps_grid)
    print(dict_timestamps_solar)

    bus_energy_levels = []
    timestamps = []
    # append the value of the first entry of data_bus_1 to bus_energy_levels and the min_time_stamp to timestamps
    bus_energy_levels.append(data_bus_1.iloc[0]['value'])
    timestamps.append(min_time_stamp)
    print(bus_energy_levels)
    print(timestamps)

    # find all the timestamps in data_grid_bus and data_solar_bus and combine them in timestamps
    # timestamps are the fourth index in variable name
    timestamps.extend(data_grid_bus['variable name'].str.split("_").str[4].astype(int))
    timestamps.extend(data_solar_bus['variable name'].str.split("_").str[4].astype(int))
    # sort the timestamps in ascending order and keep the unique ones
    timestamps = list(set(timestamps))
    timestamps = sorted(timestamps)
    print(timestamps)
    # for each timestamp in timestamps, find the corresponding grid and solar values and calculate the bus energy level
    # for each timestamp
    for timestamp in timestamps[1:]:
        if timestamp in dict_timestamps_grid.keys():
            grid_index = dict_timestamps_grid[timestamp]
            grid_value = data_grid_bus[data_grid_bus['variable index'] == grid_index]['value'].values[0]
        else:
            grid_value = 0
        if timestamp in dict_timestamps_solar.keys():
            solar_index = dict_timestamps_solar[timestamp]
            solar_value = data_solar_bus[data_solar_bus['variable index'] == solar_index]['value'].values[0]
        else:
            solar_value = 0
        bus_energy_levels.append(bus_energy_levels[-1] + grid_value + solar_value)
    print(bus_energy_levels)
    print(len(bus_energy_levels))  # take into account the dissipation due to trips
    print(len(timestamps))

    scenarios_list = []
    scenario_grid = []
    scenario_renewables = []

    for scenario in range(1, 53):
        data_grid_bus_scenario = data_variable[data_variable['variable name'].str.contains(f'x_{scenario}_')]
        data_battery_bus_scenario = data_variable[data_variable['variable name'].str.contains(f'y_{scenario}_')]
        data_grid_battery_scenario = data_variable[data_variable['variable name'].str.contains(f'h_{scenario}_')]
        grid_usage = data_grid_bus_scenario['value'].sum() + data_grid_battery_scenario['value'].sum()
        renewables_usage = data_battery_bus_scenario['value'].sum() - data_grid_battery_scenario['value'].sum()
        grid_battery_usage = data_grid_battery_scenario['value'].sum()
        scenarios_list.append(scenario)
        scenario_grid.append(grid_usage)
        scenario_renewables.append(renewables_usage)
        print(f"Scenario {scenario} grid usage = {grid_usage} kWh")
        print(f"Scenario {scenario} renewables usage = {renewables_usage} kWh")
        print(f"Scenario {scenario} grid battery usage = {grid_battery_usage} kWh")
    print(scenarios_list)
    print(scenario_grid)
    print(scenario_renewables)
    # figure size
    plt.figure(figsize=(12, 6))
    # for week wise
    print("Total grid usage = ", sum(scenario_grid))
    print("Total renewables usage = ", sum(scenario_renewables))
    print("% of renewables usage = ", sum(scenario_renewables) * 100 / (sum(scenario_grid) + sum(scenario_renewables)))

    plt.bar(scenarios_list, scenario_renewables, color='green', label='Solar Powered',
            alpha=0.5,
            bottom=scenario_grid)
    plt.bar(scenarios_list, scenario_grid, color='#FA8072', label='Grid Powered', alpha=1)

    plt.xlabel('Week of the year', fontsize=20)
    plt.ylabel('Energy (kWh)', fontsize=20)
    # increase the font size of legend
    plt.legend()
    plt.legend(fontsize=16)
    # set xticks and yticks font size
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    # save the plot to a pdf file
    plt.savefig(f'{folder_path}/{network}/{scenarios}_scenario/energy_required_{network}.pdf', dpi=300,
                bbox_inches='tight')
    plt.show()
