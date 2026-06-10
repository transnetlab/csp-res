import os
import pickle
import pandas as pd


def build_scenario(network_name: str, scenarios: int):
    """
    This function is used to build the scenario for the given network and number of scenarios
    :param network_name:  network name
    :param scenarios: number of scenarios
    :return: 
    dict_scenario: dictionary containing the GHI values for each location for each scenario at every time_stamp
    """

    # Specify the directory where your CSV files are located
    folder_path = fr'./{network_name}/{scenarios}_scenario/solar_data'

    # # Get a list of all files in the specified directory
    files = os.listdir(folder_path)

    # import charging_location.pkl
    with open(f'./{network_name}/{scenarios}_scenario/overall_charging_locations_cs.pkl', 'rb') as f:
        charging_location = set(pickle.load(f))

    # finding the file for each charging location
    dict_csv = {}
    for file in files:
        location = file.split('_')[0]
        dict_csv[location] = file

    dict_scenario = {}

    # iterating over the charging locations
    for location in charging_location:
        # convert location to string
        location = str(location)
        if network_name == 'Durham_2.1k':
            stops = pd.read_csv(f'./{network_name}/stops.txt')
            # find the stop_code for the location
            location1 = str(stops[stops.stop_id == location].stop_code.values[0])
            path = dict_csv[location1]
        else:
            # read the csv file
            path = dict_csv[location]
        df = pd.read_csv(f'./{network_name}/{scenarios}_scenario/solar_data/{path}')

        # create a dictionary for each location
        dict_scenario[location] = {}
        # average of GHI value at every hour
        for i in range(1, scenarios + 1):
            data = df[df['Scenario'] == i]
            # for each scenario
            dict_scenario[location][i] = {}
            # for each hour
            for j in range(24):
                dict_scenario[location][i][j] = round(data[data.Hour == j]['Plane of Array '
                                                                           'Irradiance (W/m2)'].mean()/60000, 5)

    # save dict_scenario as pickle file
    with open(f'./{network_name}/{scenarios}_scenario/gti_variation.pkl', 'wb') as f:
        pickle.dump(dict_scenario, f)

    return dict_scenario
