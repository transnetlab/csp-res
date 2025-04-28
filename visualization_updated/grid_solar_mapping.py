import pickle
import pandas as pd


def map_grid_or_solar_gantt_chart(network, folder_path):
    """
    :param network: Network name
    :param folder_path: Path to the folder containing the network
    :return:
    """
    # CURR_DIR = os.path.dirname(os.path.realpath(__file__))  # current directory
    # read trip_times file in arlington network
    # network = 'Durham_2.1k'
    # folder_path = CURR_DIR[:-22]
    number_of_scenario = 52
    # open the file dict_network_name.pkl
    with open(f'{folder_path}/dict_network_name.pkl', 'rb') as f:
        dict_network_short_name = pickle.load(f)
    scenarios = [10, 26, 50]

    for scenario in scenarios:
        # load charging bess schedule
        charging_solar = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/csp_solar_{dict_network_short_name[network]}_'
            f'{scenario}_scenario.csv')
        y_variables = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/y_{scenario}_grid_or_solar.csv')
        print(scenario)
        # print(charging_solar)
        # print(y_variables)
        print(y_variables.shape[0])
        # count the number of times grid, solar and both are used in y_variables grid/solar column
        grid_count = 0
        solar_count = 0
        both_count = 0
        for i, row in y_variables.iterrows():
            if row['grid/solar'] == 'grid':
                grid_count += 1
            elif row['grid/solar'] == 'solar':
                solar_count += 1
            else:
                both_count += 1
        print(f'grid_count: {grid_count}')
        print(f'solar_count: {solar_count}')
        print(f'both_count: {both_count}')

        # create a time column in charging_solar from charging start time with time converted to minutes from midnight
        charging_solar['time'] = charging_solar['charging_start_time'].apply(
            lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
        # print(charging_solar)
        # create a new column in charging_solar called 'grid/solar actual' and update based on bus, actual location and time from the y_variables
        # charging_solar['grid/solar actual'] = 0
        for i, row in charging_solar.iterrows():
            time = row.time
            bus = row.bus_number
            location = row.stop_location
            df_filtered_y_variables = y_variables[
                (y_variables['actual_location'] == location) & (y_variables['time'] == time) & (
                        y_variables['bus'] == bus)]
            for j, row_y in df_filtered_y_variables.iterrows():
                charging_solar.at[i, 'grid_or_solar'] = row_y['grid/solar']
        # print(charging_solar)
        grid_count = 0
        solar_count = 0
        both_count = 0
        for i, row in charging_solar.iterrows():
            if row['grid_or_solar'] == 'grid':
                grid_count += 1
            elif row['grid_or_solar'] == 'solar':
                solar_count += 1
            else:
                both_count += 1
        print(f'grid_count actual: {grid_count}')
        print(f'solar_count actual: {solar_count}')
        print(f'both_count actual: {both_count}')
        # save the updated charging_solar
        charging_solar.to_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/csp_solar_{dict_network_short_name[network]}_'
            f'{scenario}_scenario_actual.csv', index=False)
