import pickle
import pandas as pd

# open the file
with open('./dict_network_name.pkl', 'rb') as f:
    dict_network_name = pickle.load(f)


def run_input_file(run_id: int):
    """
    This function is used to run the input file
    :param run_id: type of scenario to be run with different cases
    :return:
    dict_kwargs: dictionary containing the input file locations, scenarios and cases
    """
    # read the run_file
    run_file = pd.read_csv('./run_file.csv')
    (run_id, network_name, benders_strategy, apply_benders_cut, scenarios,
     variable_type, parallel_mode, use_temperature, use_renewable) = run_file.loc[run_id - 1]

    # print the input parameters
    print(f"Run ID: {run_id}")
    print(f"Network Name: {network_name}")
    print(f"Number of scenarios: {scenarios}")
    print(f"Benders cut: {apply_benders_cut}")
    print(f"Benders Strategy: {benders_strategy}")
    print(f"Variable Type: {variable_type}")
    print(f"Parallel Mode: {parallel_mode}")
    print(f'Temperature variations: {use_temperature}')
    print(f'Renewables integration: {use_renewable}')

    # location for files that are required
    file_name_trip_times = fr'./{network_name}/trip_times.csv'
    file_name_trips = fr'./{network_name}/trips.txt'
    file_name_stop_distance = f"./{network_name}/distance_file.pkl"
    file_name_terminal_stops_mapping = f"./{network_name}/dict_terminal_mapping.pkl"

    # temperature variations and without temperature
    if use_temperature:
        file_name_charging_locations = f'./{network_name}/{scenarios}_scenario/overall_charging_locations_cs.pkl'
        file_name_stops = f"./{network_name}/stops.txt"
        file_name_depot_index_to_stop = f'./{network_name}/{scenarios}_scenario/depot_index_to_stop.pkl'
    else:
        file_name_charging_locations = f'./{network_name}/without_temperature/1_scenario/overall_charging_locations_cs.pkl'
        file_name_stops = f"./{network_name}/stops.txt"
        file_name_depot_index_to_stop = f'./{network_name}/without_temperature/1_scenario/depot_index_to_stop.pkl'

    dict_kwargs_preprocessing = {'network_name': network_name,
                                 'file_name_trip_times': file_name_trip_times,
                                 'file_name_stop_distance': file_name_stop_distance,
                                 'file_name_terminal_stops_mapping': file_name_terminal_stops_mapping,
                                 'file_name_charging_locations': file_name_charging_locations,
                                 'file_name_stops': file_name_stops,
                                 'file_name_depot_index_to_stop': file_name_depot_index_to_stop,
                                 'scenarios': scenarios,
                                 'use_temperature': use_temperature
                                 }

    dict_kwargs_csp = {'network_name': network_name,
                       'scenarios': scenarios,
                       'apply_benders_cut': apply_benders_cut,
                       'benders_strategy': benders_strategy,
                       'variable_type': variable_type,
                       'parallel_mode': parallel_mode,
                       'use_temperature': use_temperature,
                       'use_renewables': use_renewable,
                       'dict_network_name': dict_network_name,
                       'probability': 1 / scenarios,
                       'run_id': run_id,
                       }

    return dict_kwargs_preprocessing, dict_kwargs_csp
