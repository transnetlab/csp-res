from week_of_month import assign_week_to_month
from datetime import date
from datetime import timedelta
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm


def assign_bus_number(bus_trip_assignment: list, trip_schedule: pd.DataFrame, scenario: int,
                      dict_start_location: dict, dict_depot_index: dict, dict_depot: dict) -> int:
    """
      assigning bus number for a given sequence of trip
      updating the trip schedule dataframe with bus number for a given scenario
      Parameters:
      ____________
      bus_trip_assignment: list of trip sequence that needs to be assigned to bus
      trip_schedule_df: DataFrame trip schedule
      scenario: scenario number
      dict_start_location: dictionary of bus number and its corresponding start location
      dict_depot_index: depot index
      dict_depot: dictionary of depot for each scenario
      Returns:
        _________
        bus - 1: number of buses required for the given scenario

      """

    # assigning bus_number to trip as per bus assignment
    print("##################################################")
    bus = 1
    trip_schedule[f'bus_number_{scenario}'] = 0

    # assigning all trips sequence to bus number
    for trip_sequence in bus_trip_assignment:

        # 1st and last index contains the depot location, ignoring them while assigning bus number
        for trip in trip_sequence[1:-1]:
            i = trip_schedule[trip_schedule.Trip_ID == trip].index.values[0]
            trip_schedule.loc[i, f'bus_number_{scenario}'] = int(bus)

        # assigning the depot location to the bus number for the given scenario
        dict_start_location[scenario][bus] = str(dict_depot_index[trip_sequence[0]])

        # incrementing the bus number
        bus += 1

    # for a given scenario storing all the depots in the dictionary
    dict_depot[scenario] = set(dict_start_location[scenario].values())

    # printing the number of buses required for the given scenario
    print(f"Number of buses required for the scenario {scenario}: ", bus - 1)

    return bus - 1


def assign_bus(file_name_trip_times, file_name_depot_index_to_stop, network_name, scenarios, use_temperature=True):
    """
    :param file_name_trip_times: trip times file location
    :param file_name_depot_index_to_stop: depot index file location
    :param scenarios: number of scenarios
    :param network_name: network name
    :param use_temperature: boolean value whether temperature variations considered or not
    :return:
    dict_time_stamp: dictionary of bus number and time stamp
    dict_charging_event_wise_time_stamp: dictionary of bus number and charging event wise time stamp
    dict_bus_start_time: dictionary of bus number and start time
    dict_energy_required: dictionary of bus number, charging location and energy required
    solar_energy_dict: dictionary of solar energy produced in each time period
    greedy_approach: boolean value whether overnight charging for all buses is possible or not
    end_time_stamp: end time stamp
    charging_locations: list of charging location
    """

    trip_schedule_df = pd.read_csv(file_name_trip_times)

    with open(file_name_depot_index_to_stop, 'rb') as file:
        dict_depot_index = pickle.load(file)

    # converting the start time and end time to datetime format
    for index, row in trip_schedule_df.iterrows():
        if row.Start_Day == 1:
            trip_schedule_df.loc[index, "Start_Time"] = str(int(row.Start_Time[:2]) - 24) + row.Start_Time[2:]
        if row.End_Day == 1:
            trip_schedule_df.loc[index, "End_Time"] = str(int(row.End_Time[:2]) - 24) + row.End_Time[2:]

    # initializing the start time and day of the model
    date_string = str(date.today())
    mid_night = np.datetime64(date_string + ' ' + '00:00:00')
    day_before_string = str(date.today() - timedelta(days=1))
    day_before_mid_night = np.datetime64(day_before_string + ' ' + '00:00:00')
    next_day_string = str(date.today() + timedelta(days=1))

    #  adding date to the time string
    trip_schedule_df.Start_Time = np.where(trip_schedule_df.Start_Day == 0,
                                           date_string + " " + trip_schedule_df.Start_Time,
                                           next_day_string + " " + trip_schedule_df.Start_Time)

    trip_schedule_df.End_Time = np.where(trip_schedule_df.End_Day == 0,
                                         date_string + " " + trip_schedule_df.End_Time,
                                         next_day_string + " " + trip_schedule_df.End_Time)

    # converting the start time and end time to datetime format
    trip_schedule_df["Start_Time"] = pd.to_datetime(trip_schedule_df["Start_Time"], format='%Y-%m-%d %H:%M:%S').copy()
    trip_schedule_df["End_Time"] = pd.to_datetime(trip_schedule_df["End_Time"], format='%Y-%m-%d %H:%M:%S').copy()

    # calculating the duration of the trip in minutes
    trip_schedule_df["duration_in_min"] = (trip_schedule_df["End_Time"] - trip_schedule_df[
        "Start_Time"]).dt.total_seconds() / 60

    # assigning bus_number to trip as per bus assignment
    dict_start_location = {}
    dict_depot = {}
    average_bus_required = 0
    # assigning bus number to trip if temperature variations are considered
    if use_temperature:
        for scenario in tqdm(range(1, scenarios + 1), desc="Assigning bus number to trip"):

            # initializing dictionary for each scenario for start location
            dict_start_location[scenario] = {}

            # loading the bus trip assignment from the pkl file
            with open(f'./{network_name}/{scenarios}_scenario/bus_rotations/'
                      f'scenario_{scenario}_bus_rotations_cs.pkl', 'rb') as f:
                bus_trip_assign = pickle.load(f)

            # updating the trip_schedule_df dataframe with bus number for a given scenario to find the bus number
            bus_required = assign_bus_number(bus_trip_assign,
                                             trip_schedule_df,
                                             scenario,
                                             dict_start_location,
                                             dict_depot_index,
                                             dict_depot)
            average_bus_required += bus_required

    # assigning bus number to trip if temperature variations are not considered, same for all scenarios
    else:
        with open(f'./{network_name}/without_temperature/1_scenario/bus_rotations/scenario_1_'
                  f'bus_rotations_cs.pkl', 'rb') as f:
            bus_trip_assign = pickle.load(f)

        # for each scenario
        for scenario in tqdm(range(1, scenarios + 1), desc="Assigning bus number to trip"):

            # initializing dictionary for each scenario for start location
            dict_start_location[scenario] = {}

            # assigning bus number to trip
            bus_required = assign_bus_number(bus_trip_assign,
                                             trip_schedule_df,
                                             scenario,
                                             dict_start_location,
                                             dict_depot_index,
                                             dict_depot)
            average_bus_required += bus_required

    # print the average number of buses required
    print("Average number of buses required: ", average_bus_required / scenarios)

    return trip_schedule_df


# scenario mapping
scenario_mapping = dict()
scenario_mapping[1] = {1: list(range(1, 53))}
months_assigned = [[1, 2, 11, 12], [5, 6, 7, 8], [3, 4, 9, 10]]
# assign week to month
year = 2024
week_month_map = assign_week_to_month(year)

scenario_mapping[3] = {}
for scenario, months in enumerate(months_assigned):
    scenario_mapping[3][scenario + 1] = []
    for month in months:
        scenario_mapping[3][scenario + 1].extend([week for week, month_assigned in week_month_map.items() if month_assigned == month])

scenario_mapping[12] = {}
for month in range(1, 13):
    scenario_mapping[12][month] = [week for week, month_assigned in week_month_map.items() if month_assigned == month]

scenario_mapping[52] = {}
for week in range(1, 53):
    scenario_mapping[52][week] = [week]


# taking parameters from the input file
Scenarios_list = [1, 3, 12, 52]
Temperature = True
network = 'Surat'
# print the input parameters
print(f"Network Name: {network}")
print(f"Number of scenarios: {Scenarios_list}")
print(f'Temperature variations: {Temperature}')
folder_path = 'E:/PycharmProjects/CSP-Benders'

# from trip_schedule find number of buses required for each scenario
number_of_buses = {}

for scenarios in Scenarios_list:
    number_of_buses[scenarios] = {}
    # location for files that are required
    trip_times_file = fr'./{network}/trip_times.csv'
    trips_file = fr'./{network}/trips.txt'
    stop_distance_file = f"./{network}/distance_file.pkl"
    terminal_stop_file = f"./{network}/dict_terminal_mapping.pkl"

    # temperature variations and without temperature
    if Temperature:
        charging_location_file = f'./{network}/{scenarios}_scenario/overall_charging_locations_cs.pkl'
        stops_file = f"./{network}/stops.txt"
        depot_index_file = f'./{network}/{scenarios}_scenario/depot_index_to_stop.pkl'
    else:
        charging_location_file = f'./{network}/without_temperature/1_scenario/overall_charging_locations_cs.pkl'
        stops_file = f"./{network}/stops.txt"
        depot_index_file = f'./{network}/without_temperature/1_scenario/depot_index_to_stop.pkl'

    # data processing step
    trip_schedule_df = assign_bus(trip_times_file, depot_index_file, network, scenarios, Temperature)

    mappings = list(scenario_mapping[scenarios].values())
    for scenario, i in enumerate(mappings):
        for value in i:
            number_of_buses[scenarios][value] = len((trip_schedule_df[f'bus_number_{scenario+1}']).unique())
            print(value, number_of_buses[scenarios][value])

# create a scatter plot for number of buses required for each scenario
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# create a dataframe
color_dict = {52: 'red', 12: 'blue', 3: 'green', 1: 'yellow'}
# create a scatter plot
plt.figure(figsize=(10, 10))
for scenarios in Scenarios_list:
    df = pd.DataFrame(number_of_buses[scenarios].items(), columns=['Scenario', 'Number of Buses'])
    # connect the points with line and add a marker at each point
    sns.lineplot(x='Scenario', y='Number of Buses', data=df, color=color_dict[scenarios], label=f'{scenarios} scenarios',
                 linewidth=2)
# plt.title('Number of buses required for each scenario')
# on y-axis don't keep decimal points
plt.yticks(range(490, 514))
plt.xticks(range(1, 53, 5))
# increase x and y ticks font size
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('Week of the Year', fontsize=20)
plt.ylabel('Number of Buses', fontsize=20)
# add legend corresponding to each scenario and color
plt.legend()
# increase the font size of legend
plt.legend(fontsize=16)
# save the plot
plt.savefig(f'{folder_path}/{network}/visualization/number_of_buses_{network}.pdf', bbox_inches='tight')
plt.show()

# from trip_schedule find the maximum duration of trip
trip_id_max_duration = trip_schedule_df['Trip_ID'][trip_schedule_df['duration_in_min'].idxmax()]

dict_trip = {}
for scenarios in Scenarios_list:
    dict_trip[scenarios] = {}
    mappings = list(scenario_mapping[scenarios].values())
    for scenario, i in enumerate(mappings):
        with open(f'{folder_path}/{network}/{scenarios}_scenario/energy_consumption_trip/scenario_{scenario + 1}_energy_consumption_trips.pkl', 'rb') as f:
            dict_trip_energy = pickle.load(f)
        for value in i:
            dict_trip[scenarios][value] = dict_trip_energy[trip_id_max_duration]
            print(value, dict_trip[scenarios][value])

# PLOT A SCATTER PLOT FOR ENERGY CONSUMPTION OF TRIP WITH MAXIMUM DURATION
# create a scatter plot
plt.figure(figsize=(10, 10))
for scenarios in Scenarios_list:
    # create a dataframe
    df = pd.DataFrame(dict_trip[scenarios].items(), columns=['Scenario', 'Energy Consumption'])
    # connect the points with line and add a marker at each point
    sns.lineplot(x='Scenario', y='Energy Consumption', data=df, color=color_dict[scenarios], label=f'{scenarios} scenarios',
                 linewidth=2)
# plt.title('Energy consumption of trip with maximum duration')
# on y-axis don't keep decimal points
plt.yticks(range(25, 35))
plt.xticks(range(1, 53, 5))
# increase x and y ticks font size
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('Week of the Year', fontsize=20)
plt.ylabel('Energy Consumption', fontsize=20)
# add legend
plt.legend()
# increase the font size of legend
plt.legend(fontsize=16)
# save the plot
plt.savefig(f'{folder_path}/{network}/visualization/energy_consumption_trip_{network}_{trip_id_max_duration}.pdf', bbox_inches='tight')
plt.show()
