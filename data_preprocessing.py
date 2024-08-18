import pickle
from datetime import date
from datetime import timedelta

import numpy as np
import pandas as pd
from haversine import haversine, Unit
from tqdm import tqdm


# stop to stop distance function
def stop_to_stop_distance(stop_id_1: str, stop_id_2: str, dict_stop_distance: dict, stops_df: pd.DataFrame) -> float:
    """
    Calculate distance between two stops
    :param stop_id_1: stop id 1
    :param stop_id_2: stop id 2
    :param dict_stop_distance: dictionary of stop distance
    :param stops_df: stops dataframe
    :return:
    distance between two stops
    """
    # check if distance is available in the dictionary from stop_id_1 to stop_id_2
    if (stop_id_1, stop_id_2) in dict_stop_distance:
        distance = dict_stop_distance[(stop_id_1, stop_id_2)]

    # elif check if distance is available in the dictionary from stop_id_2 to stop_id_1
    elif (stop_id_2, stop_id_1) in dict_stop_distance:
        distance = dict_stop_distance[(stop_id_2, stop_id_1)]

    # else find the distance between the two stops using haversine formula
    else:
        stop_1_lat = stops_df[stops_df.stop_id == np.int64(stop_id_1)].stop_lat.values[0]
        stop_1_lon = stops_df[stops_df.stop_id == np.int64(stop_id_1)].stop_lon.values[0]
        stop_2_lat = stops_df[stops_df.stop_id == np.int64(stop_id_2)].stop_lat.values[0]
        stop_2_lon = stops_df[stops_df.stop_id == np.int64(stop_id_2)].stop_lon.values[0]

        # using haversine module/package to calculate distance between two points
        distance = haversine((stop_1_lat, stop_1_lon), (stop_2_lat, stop_2_lon), unit=Unit.KILOMETERS)

    return distance


def assign_bus_number(bus_trip_assignment: list, trip_schedule_df: pd.DataFrame, scenario: int,
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
    trip_schedule_df[f'bus_number_{scenario}'] = 0

    # assigning all trips sequence to bus number
    for trip_sequence in bus_trip_assignment:

        # 1st and last index contains the depot location, ignoring them while assigning bus number
        for trip in trip_sequence[1:-1]:
            i = trip_schedule_df[trip_schedule_df.Trip_ID == trip].index.values[0]
            trip_schedule_df.loc[i, f'bus_number_{scenario}'] = int(bus)

        # assigning the depot location to the bus number for the given scenario
        dict_start_location[scenario][bus] = str(dict_depot_index[trip_sequence[0]])

        # incrementing the bus number
        bus += 1

    # for a given scenario storing all the depots in the dictionary
    dict_depot[scenario] = set(dict_start_location[scenario].values())

    # printing the number of buses required for the given scenario
    print(f"Number of buses required for the scenario {scenario}: ", bus - 1)

    return bus - 1


def calculate_time_stamps_and_charging_opportunity(trip_schedule_df: pd.DataFrame,
                                                   stops_df: pd.DataFrame,
                                                   dict_stop_to_stop_distances: dict,
                                                   charging_locations: set,
                                                   dict_start_location: dict,
                                                   reference_start_time: np.datetime64,
                                                   number_of_scenarios: int,
                                                   dict_terminal_stop_mapping: dict,
                                                   average_bus_deadheading_speed=30) -> (dict, dict):
    """
    Assigning time stamp, charging opportunity to buses based on trip schedule and location
    :param trip_schedule_df: trip schedule dataframe
    :param stops_df: stops dataframe
    :param dict_stop_to_stop_distances: dictionary of stop to stop distances
    :param charging_locations: set of charging location
    :param dict_start_location: dictionary of bus number and corresponding start location for each scenario
    :param reference_start_time: reference start time to calculate time stamp
    :param average_bus_deadheading_speed: average speed of bus in km/hr
    :param number_of_scenarios: number of scenarios
    :param dict_terminal_stop_mapping: dictionary of mapping terminal stop to cluster's stop

    :return:
    dict_time_stamp: dictionary of scenario wise bus its time stamp and corresponding charging event and location
    dict_charging_event_wise_time_stamp: dictionary of scenario wise bus its charging event
                                         and corresponding time stamps
    """

    dict_time_stamp = {}
    dict_charging_event_wise_time_stamp = {}

    # number of minutes in hour
    time_step_hour = 60

    # iterating over each scenario
    for scenario in tqdm(range(1, number_of_scenarios + 1), desc=f"Assigning time stamp to buses"):

        # initializing dictionary for each scenario
        dict_time_stamp[scenario], dict_charging_event_wise_time_stamp[scenario] = {}, {}

        # list of bus number in the scenario
        bus_list = trip_schedule_df[f'bus_number_{scenario}'].unique()

        # for each bus
        for bus in bus_list:

            # initializing dictionary for each bus for that scenario
            dict_time_stamp[scenario][bus] = {}
            dict_charging_event_wise_time_stamp[scenario][bus] = {}

            # first charging opportunity
            charging_opportunity = 1

            # copy the bus schedule for the given scenario
            bus_schedule = trip_schedule_df[trip_schedule_df[f'bus_number_{scenario}'] == bus].copy()

            # start location of bus for the given scenario
            previous_stop = dict_start_location[scenario][bus]

            # updated previous_stop of bus based on clustering of terminal stops
            try:
                updated_previous_stop = str((dict_terminal_stop_mapping[previous_stop]))
            except KeyError:
                updated_previous_stop = str(dict_terminal_stop_mapping[int(previous_stop)])

            # schedule end time of the bus
            schedule_end_time = bus_schedule.End_Time.tail(1).values[0]

            # end stop of the bus schedule
            end_stop = str(bus_schedule.End_Stop.tail(1).values[0])

            # for overnight charging, end time of the bus schedule is the start time of the bus schedule for charging
            charging_start_time = (schedule_end_time - np.timedelta64(1, "D"))
            # checking if updated previous stop is not equal to previous stop

            # deadheading distance between the end stop of last trip and depot
            deadhead_distance = round(stop_to_stop_distance(end_stop, previous_stop, dict_stop_to_stop_distances,
                                                            stops_df), 3)

            # time_taken_to_reach_depot (in minutes) is time required to complete the deadheading distance
            # from previous end stop to depot
            time_taken_to_reach_depot = np.ceil((deadhead_distance * time_step_hour) / average_bus_deadheading_speed)

            # updating the charging start time
            charging_start_time = charging_start_time + np.timedelta64(int(time_taken_to_reach_depot), 'm')

            # iterating over each trip in bus schedule
            for ind, r in bus_schedule.iterrows():

                # start stop of the trip
                start_stop = r.Start_Stop

                # checking if type of start stop is float then converting it to string
                if type(start_stop) is np.float64:
                    start_stop = str(int(start_stop))
                else:
                    start_stop = str(start_stop)

                # deadheading to start of first trip
                deadhead_distance = round(stop_to_stop_distance(previous_stop, start_stop,
                                                                dict_stop_to_stop_distances, stops_df), 3)

                # time_taken_to_complete_next_deadhead (in minutes) is time required to complete the deadheading distance
                # from previous end stop to start stop
                time_taken_to_complete_next_deadhead = np.ceil((deadhead_distance * time_step_hour) / average_bus_deadheading_speed)

                # extra time for deadheading to new terminal based on clustering, adding extra time if updated previous stop
                # is not equal to previous stop for deadheading to new terminal (we have considered maximum 500 meters)
                if updated_previous_stop != previous_stop:
                    extra_time_for_deadheading_to_new_terminal = 1
                    previous_stop = updated_previous_stop
                else:
                    extra_time_for_deadheading_to_new_terminal = 0

                # checking if previous stop is charging location, and initializing list of time stamp for available time
                if previous_stop in charging_locations:

                    # initializing list of time stamp for each charging event
                    dict_charging_event_wise_time_stamp[scenario][bus][charging_opportunity] = []

                    # time stamp for start of the charging event with respect to reference midnight time
                    time_stamp = int((charging_start_time - reference_start_time) / np.timedelta64(1, 'm'))

                    # total available time for the bus as per schedule between the end stop and next start stop of trip.
                    # also removing the extra time for deadheading to new terminal
                    total_available_time = (int((r.Start_Time - charging_start_time) / np.timedelta64(1, 'm'))
                                            - extra_time_for_deadheading_to_new_terminal)

                    # adding timestamp if total available time is greater than time taken by the bus to cover the
                    # deadheading distance between the end stop of last trip and start stop of next trip
                    if int(total_available_time - time_taken_to_complete_next_deadhead) > 0:
                        for x in range(int(total_available_time - time_taken_to_complete_next_deadhead)):
                            dict_time_stamp[scenario][bus][time_stamp] = (charging_opportunity, previous_stop)
                            dict_charging_event_wise_time_stamp[scenario][bus][charging_opportunity].append(time_stamp)
                            time_stamp += 1

                    # adding the charging location to the end of the list of time stamp
                    dict_charging_event_wise_time_stamp[scenario][bus][charging_opportunity].append(previous_stop)

                    # incrementing the charging event
                    charging_opportunity += 1

                # if start stop is charging location then initialize list of time stamp for each charging event
                elif start_stop in charging_locations:

                    # initializing list of time stamp for each charging event
                    dict_charging_event_wise_time_stamp[scenario][bus][charging_opportunity] = []

                    # adding the time taken to the time stamp if start stop is charging location.
                    time_stamp = (int((charging_start_time - reference_start_time) / np.timedelta64(1, 'm'))
                                  + int(time_taken_to_complete_next_deadhead))
                    total_available_time = int((r.Start_Time - charging_start_time) / np.timedelta64(1, 'm'))

                    if int(total_available_time - time_taken_to_complete_next_deadhead) > 0:
                        for x in range(int(total_available_time - time_taken_to_complete_next_deadhead)):
                            dict_time_stamp[scenario][bus][time_stamp] = (charging_opportunity, start_stop)
                            dict_charging_event_wise_time_stamp[scenario][bus][charging_opportunity].append(time_stamp)
                            time_stamp += 1

                    # adding the charging location to the end of the list of time stamp
                    dict_charging_event_wise_time_stamp[scenario][bus][charging_opportunity].append(start_stop)

                    # incrementing the charging event
                    charging_opportunity += 1

                # updating the previous stop to the end stop of the trip
                previous_stop = r.End_Stop

                # updating the charging start time to the end time of the trip
                charging_start_time = r.End_Time

                # updating the updated previous stop to the end stop of the trip based on clustering
                try:
                    updated_previous_stop = str((dict_terminal_stop_mapping[previous_stop]))
                except KeyError:
                    updated_previous_stop = str(dict_terminal_stop_mapping[int(previous_stop)])
                if type(previous_stop) is np.float64:
                    previous_stop = str(int(previous_stop))
                else:
                    previous_stop = str(previous_stop)

    return dict_time_stamp, dict_charging_event_wise_time_stamp


def estimate_charging_opportunity_wise_energy_requirement(trip_schedule_df: pd.DataFrame,
                                                          dict_charging_event_wise_time_stamp: dict,
                                                          charging_locations: set,
                                                          number_of_scenarios: int,
                                                          network: str,
                                                          dict_depot_index: dict,
                                                          dict_terminal_mapping: dict,
                                                          temperature=True) -> dict:
    """
    :param trip_schedule_df: trip schedule dataframe
    :param dict_charging_event_wise_time_stamp: dictionary of scenario wise bus its charging event
                                                and corresponding time stamps
    :param charging_locations: set of charging locations
    :param number_of_scenarios: total number of scenarios
    :param network: network name
    :param dict_depot_index: dictionary of depot index
    :param dict_terminal_mapping: dictionary of mapping cluster to terminal
    :param temperature: boolean value whether temperature variations considered or not

    :return:
    dict_energy_required: dictionary of scenarios-wise energy required for every charging opportunity for each bus
    """
    dict_energy_required = {}

    # location of files for energy consumption data should be in the same directory
    # if temperature variations are not considered, loading the energy consumption data from the pkl file only once.
    if not temperature:
        with open(f'./{network}/without_temperature/1_scenario/'
                  f'energy_consumption_trip/scenario_1_energy_consumption_trips.pkl', 'rb') as f:
            dict_trip_energy = pickle.load(f)
        with open(f'./{network}/without_temperature/1_scenario/'
                  f'energy_consumption_deadhead/scenario_1_energy_consumption_deadhead.pkl', 'rb') as f:
            dict_deadhead_energy = pickle.load(f)

    # for each scenario
    for scenario in tqdm(range(1, number_of_scenarios + 1), desc="Calculating energy required for each bus"):

        # initializing dictionary for each scenario
        dict_energy_required[scenario] = {}

        # list of bus number in the scenario
        bus_list = trip_schedule_df[f'bus_number_{scenario}'].unique()

        # if temperature variations are considered, loading the energy consumption data from the pkl file for scenario
        if temperature:
            # open the file in pkl format for trip energy requirement
            with open(f'./{network}/{number_of_scenarios}_scenario/energy_consumption_trip/'
                      f'scenario_{scenario}_energy_consumption_trips.pkl', 'rb') as f:
                dict_trip_energy = pickle.load(f)

            # open the file in pkl format for deadhead energy requirement
            with open(f'./{network}/{number_of_scenarios}_scenario/energy_consumption_deadhead/'
                      f'scenario_{scenario}_energy_consumption_deadhead.pkl', 'rb') as f:
                dict_deadhead_energy = pickle.load(f)

        # for each bus in the scenario
        for bus in bus_list:

            # initializing dictionary for each bus for that scenario
            dict_energy_required[scenario][bus] = {}

            # copy the bus schedule for the bus
            bus_schedule = trip_schedule_df[trip_schedule_df[f'bus_number_{scenario}'] == bus].copy()

            # first charging opportunity
            charging_opportunity = 1

            # for given charging opportunity in the bus schedule, first charging stop is the depot
            first_charging_stop = dict_charging_event_wise_time_stamp[scenario][bus][charging_opportunity][-1]

            # updating the first charging stop to the terminal based on clustering
            try:
                updated_previous_stop = str((dict_terminal_mapping[first_charging_stop]))
            except KeyError:
                updated_previous_stop = str(dict_terminal_mapping[int(first_charging_stop)])
            if updated_previous_stop != first_charging_stop:
                first_charging_stop = updated_previous_stop
            else:
                pass
            # if the network is Durham_2.1k, then the format is string
            if network == 'Durham_2.1k':
                previous_charging_stop = str()
                # find the key corresponding to the first charging stop value in depot index dictionary
                for key, value in dict_depot_index.items():
                    if value == str(first_charging_stop):
                        previous_charging_stop = key
                        break
            else:
                previous_charging_stop = int()
                # find the key corresponding to the first charging stop value in depot index dictionary
                for key, value in dict_depot_index.items():
                    if value == int(first_charging_stop):
                        previous_charging_stop = key
                        break

            # adding deadheading stop to the dataframe to calculate deadhead energy required
            bus_schedule['deadheading_trip'] = bus_schedule.Trip_ID.shift(1).fillna(previous_charging_stop)

            # make it as int type
            bus_schedule['deadheading_trip'] = bus_schedule['deadheading_trip'].astype(int)

            # adding next deadheading stop to the dataframe for considering if start stop is charging location
            bus_schedule['start_deadheading_stop'] = bus_schedule.Start_Stop.shift(-1).fillna(first_charging_stop)
            bus_schedule['start_deadheading_trip'] = bus_schedule.Trip_ID.shift(-1).fillna(previous_charging_stop)

            # make it as int type
            bus_schedule['start_deadheading_trip'] = bus_schedule['start_deadheading_trip'].astype(int)

            # initializing the deadhead_trip_distance to 0
            deadhead_trip_distance = 0

            # adding flag to check if start stop is charging location
            flag = True

            # re-index the dataframe
            bus_schedule.reset_index(drop=True, inplace=True)

            # for each trip in the bus schedule
            for index, row in bus_schedule.iterrows():

                # end stop of the trip
                end_stop = str(row.End_Stop)

                # updating the end stop to the terminal based on clustering
                try:
                    updated_end_stop = str((dict_terminal_mapping[end_stop]))
                except KeyError:
                    updated_end_stop = str(dict_terminal_mapping[int(end_stop)])
                if updated_end_stop != end_stop:
                    end_stop = updated_end_stop
                else:
                    pass

                # trip name for the trip
                trip = row.Trip_ID
                try:
                    previous_dead_trip = str(int(row.deadheading_trip))
                    next_dead_stop = str(int(row.start_deadheading_stop))
                    next_dead_trip = str(int(row.start_deadheading_trip))
                except ValueError:
                    previous_dead_trip = str(row.deadheading_trip)
                    next_dead_stop = str(row.start_deadheading_stop)
                    next_dead_trip = str(row.start_deadheading_trip)

                # updating the deadheading stop to the terminal based on clustering
                try:
                    updated_next_dead_stop = str((dict_terminal_mapping[next_dead_stop]))
                except KeyError:
                    updated_next_dead_stop = str(dict_terminal_mapping[int(next_dead_stop)])
                if updated_next_dead_stop != next_dead_stop:
                    next_dead_stop = updated_next_dead_stop
                else:
                    pass

                # when flag is false it will avoid adding distance between start stop and charging location because
                # we have already added deadhead distance in condition of start stop being charging location and
                # flag will become true again
                if flag:
                    deadhead_trip_distance += round(dict_deadhead_energy[(int(previous_dead_trip), trip)], 3)
                else:
                    deadhead_trip_distance += 0
                    flag = True

                # adding energy required for the given trip
                deadhead_trip_distance += round(dict_trip_energy[trip], 3)

                # adding energy required for charging event if end stop is charging location to last charging location
                # taking the instance in dataframe where its possible that last end stop is not charging location
                if (end_stop in charging_locations) or (index == len(bus_schedule) - 1):

                    if index == len(bus_schedule) - 1:
                        deadhead_trip_distance += round(dict_deadhead_energy[(trip, int(previous_charging_stop))], 3)

                    # rounding the energy required to 3 decimal places
                    dict_energy_required[scenario][bus][charging_opportunity] = round(deadhead_trip_distance, 3)

                    # initializing the deadhead_trip_distance to 0
                    deadhead_trip_distance = 0

                    # incrementing the charging opportunity
                    charging_opportunity += 1

                # adding energy required for charging event if start stop is charging location
                elif next_dead_stop in charging_locations:

                    # find the key corresponding to the next deadheading stop value in depot index dictionary
                    deadhead_trip_distance += round(dict_deadhead_energy[(trip, int(next_dead_trip))], 3)

                    # rounding the energy required to 3 decimal places
                    dict_energy_required[scenario][bus][charging_opportunity] = round(deadhead_trip_distance, 3)

                    # initializing the deadhead_trip_distance to 0
                    deadhead_trip_distance = 0

                    # incrementing the charging opportunity
                    charging_opportunity += 1

                    # setting flag to false
                    flag = False

    return dict_energy_required


def find_time_stamp_grid(start_time: dict, end_time: int, dict_time_stamp: dict, scenarios: int) -> dict:
    """
    Finding time-steps for grid capacity constraints and corresponding buses charging at that time stamp
    :param start_time: dict of start time of charging event for each scenario
    :param end_time: end time of charging event
    :param dict_time_stamp: dictionary of scenario wise bus its time stamp and corresponding charging event and location
    :param scenarios: number of scenarios
    :return:
    dict_time_stamp_grid: dictionary of time stamp and number of buses charging at that time stamp at location
    """

    # initializing dictionary
    dict_time_stamp_grid = {}

    # for each scenario
    for scenario in tqdm(range(1, scenarios + 1), desc="Finding time-steps for grid capacity constraints"):

        # initializing dictionary for each scenario
        dict_time_stamp_grid[scenario] = {}

        # for each time stamp in the scenario
        for time in range(start_time[scenario], end_time + 1):

            # initializing dictionary for each time stamp
            dict_time_stamp_grid[scenario][time] = {}

            # for each bus in the scenario
            for bus, series in dict_time_stamp[scenario].items():

                # for each time stamp in the series
                for time_stamp, (charging_event, location) in series.items():

                    #  if time stamp is equal to time
                    if time_stamp == time:

                        # if location is not in the dictionary then add the location and bus to the dictionary
                        if location not in dict_time_stamp_grid[scenario][time]:
                            dict_time_stamp_grid[scenario][time][location] = [bus]

                        else:
                            dict_time_stamp_grid[scenario][time][location].append(bus)

            # removing the empty dictionary from the dictionary
            if len(dict_time_stamp_grid[scenario][time]) == 0:
                del dict_time_stamp_grid[scenario][time]

    return dict_time_stamp_grid


def preprocessing(file_name_trip_times, file_name_stop_distance, file_name_charging_locations, file_name_depot_index_to_stop,
                  file_name_stops, file_name_terminal_stops_mapping, network_name, scenarios, use_temperature=True):
    """
    :param file_name_trip_times: trip times file location
    :param file_name_stop_distance: stop distance file location
    :param file_name_charging_locations: charging location file location
    :param file_name_stops: stops_df file location
    :param file_name_depot_index_to_stop: depot index file location
    :param file_name_terminal_stops_mapping: terminal mapping file location
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
    stops_df = pd.read_csv(file_name_stops)

    with open(file_name_charging_locations, 'rb') as file:
        charging_locations = pickle.load(file)

    with open(file_name_depot_index_to_stop, 'rb') as file:
        dict_depot_index = pickle.load(file)

    with open(file_name_terminal_stops_mapping, 'rb') as file:
        dict_terminal_mapping = pickle.load(file)

    # convert the location in charging_locations to string
    charging_locations = [str(i) for i in charging_locations]

    # open the file in pkl format
    with open(file_name_stop_distance, 'rb') as f:
        dict_stop_distance = pickle.load(f)

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
    start_time_non_depot = int((mid_night + np.timedelta64(5, 'h')
                                - day_before_mid_night) / np.timedelta64(1, 'm'))

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

    # start time stamp for the model will be the end time stamp of the previous day
    start_time = trip_schedule_df.End_Time.max()
    # start time w.r.t scenario
    start_time_stamp = {}
    for scenario in tqdm(range(1, scenarios + 1), desc="Finding start time stamp"):
        bus_list = list(trip_schedule_df[f'bus_number_{scenario}'].unique())
        for bus in bus_list:
            t = trip_schedule_df[trip_schedule_df[f'bus_number_{scenario}'] == bus].End_Time.max()
            if t <= start_time:
                start_time = t
        start_time_stamp[scenario] = int((start_time - mid_night) / np.timedelta64(1, 'm'))

    # last time stamp of the complete schedule
    end_time = trip_schedule_df.End_Time.max()
    end_time_stamp = int((end_time - day_before_mid_night) / np.timedelta64(1, 'm'))

    # copy of the trip schedule
    trip_schedule_copy = trip_schedule_df.copy()

    # printing the number of trips
    print("Number of trips: ", trip_schedule_copy.shape[0])

    # finding time stamp, charging opportunity to buses based on trip schedule and location
    dict_time_stamp, dict_charging_event_stamps = calculate_time_stamps_and_charging_opportunity(trip_schedule_copy,
                                                                                                 stops_df,
                                                                                                 dict_stop_distance,
                                                                                                 set(charging_locations),
                                                                                                 dict_start_location,
                                                                                                 day_before_mid_night,
                                                                                                 scenarios,
                                                                                                 dict_terminal_mapping)

    # calculating energy requirement per trip for each charging event
    dict_energy_required = estimate_charging_opportunity_wise_energy_requirement(trip_schedule_copy,
                                                                                 dict_charging_event_stamps,
                                                                                 set(charging_locations),
                                                                                 scenarios,
                                                                                 network_name,
                                                                                 dict_depot_index,
                                                                                 dict_terminal_mapping,
                                                                                 temperature=use_temperature)

    # finding time-steps for grid capacity constraints and corresponding buses charging at that time stamp
    dict_stamp_grid = find_time_stamp_grid(start_time_stamp,
                                           end_time_stamp,
                                           dict_time_stamp,
                                           scenarios)

    # print the average number of buses required
    print("Average number of buses required: ", average_bus_required / scenarios)

    return (dict_time_stamp, dict_charging_event_stamps, dict_energy_required, end_time_stamp,
            charging_locations, dict_stamp_grid, start_time_stamp)
