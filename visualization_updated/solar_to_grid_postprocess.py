import pandas as pd
import pickle


# CURR_DIR = os.path.dirname(os.path.realpath(__file__))
# folder_path = CURR_DIR[:-22]
# print(folder_path)


def postprocess_solar_to_grid(network, folder_path):
    """
    :param network: Network name
    :param folder_path: Path to the folder containing the network
    :return:
    """
    number_of_scenario = 52
    dict_network_short_name = ['durham', 'can1']
    scenario_list = [10, 26, 50]
    # network = 'Durham_2.1k'
    if network == 'Durham_2.1k':
        index_net = 0
    else:
        index_net = 1

    for scenario in scenario_list:
        print(scenario)
        # load charging schedule
        charging_grid = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/csp_{dict_network_short_name[index_net]}'
            f'_{scenario}_scenario.csv')

        # load charging solar schedule
        charging_solar = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/csp_solar_{dict_network_short_name[index_net]}_'
            f'{scenario}_scenario.csv')

        bess_to_bus_df = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/bess_to_bus_{dict_network_short_name[index_net]}_{scenario}_scenario.csv')

        bess_energy_levels_df = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/bess_energy_levels_{dict_network_short_name[index_net]}_{scenario}_scenario.csv')

        grid_to_bess_df = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/grid_to_bess_{dict_network_short_name[index_net]}_{scenario}_scenario.csv')

        grid_to_bus_df = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/grid_to_bus_{dict_network_short_name[index_net]}_{scenario}_scenario.csv')

        print(charging_grid)
        print(charging_solar)
        print(bess_to_bus_df)
        print(bess_energy_levels_df)
        print(grid_to_bess_df)
        print(grid_to_bus_df)

        df_h = pd.DataFrame(columns=['variable_name', 'location', 'time', 'value'])
        for i, row in grid_to_bess_df.iterrows():
            variable_name = row.variable_name
            location = row.variable_name.split("_")[2]
            time = row.variable_name.split("_")[3]
            value = row.value
            df_h.loc[i] = [variable_name, location, time, value]
        df_h.to_csv(f'{folder_path}/{network}/{number_of_scenario}_scenario/h_{scenario}_accumulated.csv', index=False)
        print(df_h)
        # based on the location, find the accumulated value
        # group by time_stamp and status
        df_h_grouped = df_h.groupby(['location', 'time']).agg({'value': 'sum'}).reset_index()
        # Ensure 'value' is numeric
        df_h_grouped['value'] = pd.to_numeric(df_h_grouped['value'], errors='coerce')
        # print(df_h_grouped)
        # Now apply cumsum
        df_h_grouped['accumulated_value'] = df_h_grouped.groupby('location')['value'].cumsum()
        print(df_h_grouped)
        df_h_grouped.to_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/h_{scenario}_grouped_accumulated.csv',
            index=False)
        # open .pkl file
        with open(f'{folder_path}/{network}/{number_of_scenario}_scenario/gti_variation.pkl', 'rb') as f:
            gti_variation = pickle.load(f)
        # print(gti_variation)
        # create a dictionary of df_h values with key as location and time
        dict_h = {}
        for i, row in df_h_grouped.iterrows():
            location = row.location
            time = row.time
            value = row.value
            if location not in dict_h:
                dict_h[location] = {}
            dict_h[location][time] = value
        print(dict_h)
        # print(dict_h['1163:1'][str(1146 + 4)])

        df_v = pd.DataFrame(columns=['variable_name', 'location', 'time', 'bess_energy_level'])
        for i, row in bess_energy_levels_df.iterrows():
            variable_name = row.variable_name
            location = row.variable_name.split("_")[2]
            time = row.variable_name.split("_")[3]
            # value = round(row.value, 6)
            value = row.value
            df_v.loc[i] = [variable_name, location, time, value]
        df_v.to_csv(f'{folder_path}/{network}/{number_of_scenario}_scenario/v_{scenario}_accumulated.csv', index=False)
        print(df_v)
        # find number of unique locations
        unique_locations = df_v.location.unique()
        print(len(unique_locations))
        # for every location, find the smallest and largest time from df_v and store them in a dictionary
        dict_time_info = {}
        for location in unique_locations:
            # time = df_v[df_v['location'] == location]['time']
            # dict_time_info[location] = [min(time), max(time)]
            dict_time_info[location] = [0, 1439]
        print(dict_time_info)
        # create another column in df_v to store the dict_h values
        df_v['grid_to_bess'] = 0
        # for every location, find the time in df_h and store it in df_v
        for i, row in df_v.iterrows():
            location = row.location
            if row.time == str(dict_time_info[location][1]):
                time = str(dict_time_info[location][0])
            else:
                time = str(int(row.time) + 1)
            # use default value 0 if time is not present in dict_h corresponding to the location
            # df_v.at[i, 'grid_to_bess'] = round(dict_h.get(location, {}).get(time, 0), 6)
            df_v.at[i, 'grid_to_bess'] = dict_h.get(location, {}).get(time, 0)
        print(df_v)
        df_v.to_csv(f'{folder_path}/{network}/{number_of_scenario}_scenario/v_{scenario}_accumulated.csv', index=False)

        # for bess_to_bus_df, create df_y
        df_y = pd.DataFrame(columns=['variable_name', 'bus', 'location', 'time', 'value'])
        for i, row in bess_to_bus_df.iterrows():
            variable_name = row.variable_name
            bus = row.variable_name.split("_")[2]
            location = row.variable_name.split("_")[3]
            time = row.variable_name.split("_")[4]
            value = row.value
            df_y.loc[i] = [variable_name, bus, location, time, value]
        df_y.to_csv(f'{folder_path}/{network}/{number_of_scenario}_scenario/y_{scenario}_accumulated.csv', index=False)
        # create a dictionary with key as location and time and value as total value over buses
        dict_y = {}
        for i, row in df_y.iterrows():
            location = row.location
            time = row.time
            value = row.value
            if location not in dict_y:
                dict_y[location] = {}
            if time not in dict_y[location]:
                dict_y[location][time] = 0
            # dict_y[location][time] += round(value, 6)
            dict_y[location][time] += value
        print(dict_y)

        # create df_x for grid_to_bus_df
        df_x = pd.DataFrame(columns=['variable_name', 'bus', 'location', 'time', 'value'])
        for i, row in grid_to_bus_df.iterrows():
            variable_name = row.variable_name
            bus = row.variable_name.split("_")[2]
            location = row.variable_name.split("_")[3]
            time = row.variable_name.split("_")[4]
            value = row.value
            df_x.loc[i] = [variable_name, bus, location, time, value]
        df_x.to_csv(f'{folder_path}/{network}/{number_of_scenario}_scenario/x_{scenario}_accumulated.csv', index=False)
        # create a dictionary with key as location and time and value as total value over buses
        dict_x = {}
        for i, row in df_x.iterrows():
            location = row.location
            time = row.time
            value = row.value
            if location not in dict_x:
                dict_x[location] = {}
            if time not in dict_x[location]:
                dict_x[location][time] = 0
            # dict_x[location][time] += round(value, 6)
            dict_x[location][time] += value

        # create another column in df_v to store the solar values
        df_v['panel_to_bess'] = 0
        df_v['bess_to_bus'] = 0
        df_v['grid_to_bus'] = 0
        for i, row in df_v.iterrows():
            location = row.location
            # print(row.time)
            # print(type(row.time))
            # print(dict_time_info[location][1])
            # print(str(dict_time_info[location][1]))
            if row.time == str(dict_time_info[location][1]):
                next_time = str(dict_time_info[location][0])
            else:
                next_time = str(int(row.time) + 1)

            value = \
                df_v[(df_v['location'] == str(location)) & (df_v['time'] == str(next_time))][
                    'bess_energy_level'].values[0]

            df_v.at[i, 'panel_to_bess'] = value - row.bess_energy_level - row.grid_to_bess + dict_y.get(location,
                                                                                                        {}).get(
                next_time, 0)
            df_v.at[i, 'bess_to_bus'] = dict_y.get(location, {}).get(next_time, 0)
            df_v.at[i, 'grid_to_bus'] = dict_x.get(location, {}).get(next_time, 0)

        for i, row in df_v.iterrows():
            # make the value of panel_to_bess 0 if it is negative and add the residual to grid_to_bess
            if row.panel_to_bess < 0:
                df_v.at[i, 'grid_to_bess'] += row.panel_to_bess
                df_v.at[i, 'panel_to_bess'] = 0
        for i, row in df_v.iterrows():
            if row.grid_to_bess < 0:
                df_v.at[i, 'grid_to_bess'] = 0

        # create two more columns with accumulated sum of h_values and solar_values for each location
        df_v_grouped = df_v.groupby(['location', 'time']).agg({'panel_to_bess': 'sum'}).reset_index()
        # Ensure 'value' is numeric
        df_v_grouped['panel_to_bess'] = pd.to_numeric(df_v_grouped['panel_to_bess'], errors='coerce')
        # print(df_h_grouped)
        # Now apply cumsum
        df_v_grouped['accumulated_panel_to_bess'] = df_v_grouped.groupby('location')['panel_to_bess'].cumsum()
        print(df_v_grouped)

        print(df_v)
        df_v.to_csv(f'{folder_path}/{network}/{number_of_scenario}_scenario/v_{scenario}_accumulated.csv', index=False)
        df_v_grouped.to_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/v_{scenario}_grouped_accumulated.csv',
            index=False)
