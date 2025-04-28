# read the .sol file and extract the row and column
import os
import pickle
import pandas as pd
import numpy as np

# fetch the current directory
CURR_DIR = os.path.dirname(os.path.realpath(__file__))
print(CURR_DIR)

row_status = pd.DataFrame(columns=['row', 'status'])
column_status = pd.DataFrame(columns=['column', 'status'])

network = 'Durham_2.1k'
folder_path = CURR_DIR
scenarios = 52
temperature = True
benders = True
renewables = True

# open dict_network_name.pkl

with open(f'{folder_path}/dict_network_name.pkl', 'rb') as f:
    dict_network_name = pickle.load(f)

data = pd.read_csv(f'{folder_path}/{network}/{scenarios}_scenario/csp_{dict_network_name[network]}_{scenarios}'
                   f'_benders_True_temperature_True_renewables_True.sol',
                   delimiter="=")
data = data[24:-5]
# data column names
data.columns = ['type', 'variable', 'index', 'slack']

# remove the last 6 letters from each row in name column
data['variable'] = data['variable'].str[:-6]

# if type starts with '<constraint' then in row_status dataframe
data_constraint = data[data['type'].str.contains('<constraint name')]

# if type starts with '<variable' then in column_status dataframe
data_variable = data[data['type'].str.contains('<variable name')]

data_variable['value'] = data_variable['slack'].str[:-2].copy()
# convert str to float in value column
data_variable['value'] = data_variable['value'].astype(float)

# concatenate the x_y_variables for scenarios 4, 10, 26, 33, 41, 50 (10, 26, 50)
# list_scenarios = [4, 10, 26, 33, 41, 50]
list_scenarios = [10, 26, 50]
# x_y_variables = pd.DataFrame(columns=data_variable.columns)
# for scenario in scenarios:
#     # take data of x and y variables for scenario 1
#     x_y_variables = pd.concat([x_y_variables, data_variable[data_variable['variable'].str.contains(f"x_{scenario}_") | data_variable['variable'].str.contains(f"y_{scenario}_")]])

# print(data_variable)

for scenario in list_scenarios:
    print(scenario)
    # # take data of x and y variables for scenario
    x_y_variables = data_variable[
        data_variable['variable'].str.contains(f"x_{scenario}_") | data_variable['variable'].str.contains(
            f"y_{scenario}_")]
    h_variables = data_variable[data_variable['variable'].str.contains(f"h_{scenario}_")]
    v_variables = data_variable[data_variable['variable'].str.contains(f"v_{scenario}_")]
    y_variables = data_variable[data_variable['variable'].str.contains(f"y_{scenario}_")]
    x_variables_only = data_variable[data_variable['variable'].str.contains(f"x_{scenario}_")]

    # reindex the dataframe
    x_y_variables.reset_index(drop=True, inplace=True)
    h_variables.reset_index(drop=True, inplace=True)
    v_variables.reset_index(drop=True, inplace=True)
    y_variables.reset_index(drop=True, inplace=True)
    x_variables_only.reset_index(drop=True, inplace=True)

    # remove variable with value 0
    x_y_variables = x_y_variables[x_y_variables['value'] != 0]
    h_variables = h_variables[h_variables['value'] != 0]
    v_variables = v_variables[v_variables['value'] != 0]
    y_variables = y_variables[y_variables['value'] != 0]
    x_variables_only = x_variables_only[x_variables_only['value'] != 0]
    # find number of x and y variables
    number_of_x_variables = len(x_y_variables[x_y_variables['variable'].str.contains("x")])
    number_of_y_variables = len(x_y_variables[x_y_variables['variable'].str.contains("y")])
    number_of_h_variables = len(h_variables)
    number_of_v_variables = len(v_variables)
    number_of_y_variables_updated = len(y_variables)
    number_of_x_variables_only = len(x_variables_only)
    print("Number of x variables: ", number_of_x_variables)
    print("Number of x variables only: ", number_of_x_variables_only)
    print("Number of y variables: ", number_of_y_variables)
    print("Number of y variables updated: ", number_of_y_variables_updated)

    charge_schedule = pd.DataFrame(
        columns=['bus_number', 'start_day', 'charging_start_time', 'stop_location', 'end_day',
                 'scenario', 'grid_or_solar', 'charging_end_time'])

    grid_to_bess = pd.DataFrame(columns=['variable_name', 'value'])
    # store the h_variables names and values in grid_to_bess dataframe
    for i, row in h_variables.iterrows():
        grid_to_bess.loc[i, "variable_name"] = row.variable
        grid_to_bess.loc[i, "value"] = row.value
    # find the sum of all entries in grid_to_bess
    sum_grid_to_bess = grid_to_bess['value'].sum()
    print("Sum of grid to bess: ", sum_grid_to_bess)
    bess_energy_levels = pd.DataFrame(columns=['variable_name', 'value'])
    # store the v_variables names and values in bess_energy_levels dataframe
    for i, row in v_variables.iterrows():
        bess_energy_levels.loc[i, "variable_name"] = row.variable
        bess_energy_levels.loc[i, "value"] = row.value
    bess_to_bus = pd.DataFrame(columns=['variable_name', 'value'])
    # store the y_variables names and values in bess_to_bus dataframe
    for i, row in y_variables.iterrows():
        bess_to_bus.loc[i, "variable_name"] = row.variable
        bess_to_bus.loc[i, "value"] = row.value
    sum_bess_to_bus = bess_to_bus['value'].sum()
    print("Sum of bess to bus: ", sum_bess_to_bus)
    # save the grid_to_bess as csv
    grid_to_bess.to_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/grid_to_bess_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)
    bess_energy_levels.to_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/bess_energy_levels_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)
    bess_to_bus.to_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/bess_to_bus_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)
    grid_to_bus = pd.DataFrame(columns=['variable_name', 'value'])
    for i, row in x_variables_only.iterrows():
        grid_to_bus.loc[i, "variable_name"] = row.variable
        grid_to_bus.loc[i, "value"] = row.value
    grid_to_bus.to_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/grid_to_bus_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)

    # create a column in x_y_variables which is the fourth index of variable and named as time
    x_y_variables['time'] = x_y_variables['variable'].str.split("_").str[4]
    # convert time to int
    x_y_variables['time'] = x_y_variables['time'].astype(int)
    # sort in ascending order of time
    x_y_variables = x_y_variables.sort_values(by='time')
    # reindex the dataframe
    x_y_variables.reset_index(drop=True, inplace=True)
    print(x_y_variables)

    index = 0
    check_time = -1
    number_of_variables = 0
    index_charging_capacity = 0
    index_soc = 0
    bus_no = -1
    for i, row in x_y_variables.iterrows():
        if row.variable.split("_")[0] == 'x':
            # allocating information in variables, with consideration of charging schedule extending to next day
            time = row.variable.split("_")[4]
            if (int(time) - int(check_time) >= 1) | (bus_no != row.variable.split("_")[2]):
                # print(number_of_variables, time)
                charge_schedule.loc[index, "bus_number"] = int(row.variable.split("_")[2])
                charge_schedule.loc[index, "scenario"] = int(row.variable.split("_")[1])
                charge_schedule.loc[index, "grid_or_solar"] = "grid"
                if int(time) <= 1440:
                    # print(number_of_variables, time)
                    hour = int(row.variable.split("_")[4]) // 60
                    minute = int(row.variable.split("_")[4]) % 60
                    charge_schedule.loc[index, "start_day"] = 1
                elif (int(time) > 1440) and int(time) < 2880:
                    hour = int(row.variable.split("_")[4]) // 60 - 24
                    minute = int(row.variable.split("_")[4]) % 60 - 1
                    charge_schedule.loc[index, "start_day"] = 2
                else:
                    hour = int(row.variable.split("_")[4]) // 60 - 48
                    minute = int(row.variable.split("_")[4]) % 60 - 1
                    charge_schedule.loc[index, "start_day"] = 3
                if minute == -1:
                    minute = 59
                    if hour == 0:
                        hour = 23
                        charge_schedule.loc[index, "start_day"] -= 1
                    else:
                        hour = hour - 1
                if hour == 24:
                    hour = 0
                charge_schedule.loc[index, "charging_start_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"
                charge_schedule.loc[index, "stop_location"] = row.variable.split("_")[3]

                if index == 0:
                    print(f"Time stamp for index 0 grid = {time}")

                # for the last entry update of end time for completion of charging after plug in
                if index != 0:
                    if int(check_time) < 1440:
                        hour = int(check_time) // 60
                        minute = int(check_time) % 60 + 1
                        charge_schedule.loc[(index - 1), "end_day"] = 1
                    elif (int(check_time) >= 1440) and int(check_time) < 2880:
                        hour = int(check_time) // 60 - 24
                        minute = int(check_time) % 60
                        charge_schedule.loc[(index - 1), "end_day"] = 2
                    else:
                        hour = int(check_time) // 60 - 48
                        minute = int(check_time) % 60
                        charge_schedule.loc[(index - 1), "end_day"] = 3

                    if minute == 60:
                        minute = 0
                        if hour == 23:
                            hour = 0
                            charge_schedule.loc[(index - 1), "end_day"] += 1
                        else:
                            hour = hour + 1
                    if hour == 24:
                        hour = 0
                    charge_schedule.loc[
                        (index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

                index += 1

            # updating check time, number of variables and bus number at every iteration
            check_time = time
            bus_no = row.variable.split("_")[2]
            number_of_variables += 1

            # for the last entry update of end time of dictionary
            if number_of_variables == number_of_x_variables:
                if int(check_time) < 1440:
                    hour = int(check_time) // 60
                    minute = int(check_time) % 60 + 1
                    charge_schedule.loc[(index - 1), "end_day"] = 1
                elif (int(check_time) >= 1440) and int(check_time) < 2880:
                    hour = int(check_time) // 60 - 24
                    minute = int(check_time) % 60
                    charge_schedule.loc[(index - 1), "end_day"] = 2
                else:
                    hour = int(check_time) // 60 - 48
                    minute = int(check_time) % 60
                    charge_schedule.loc[(index - 1), "end_day"] = 3

                if minute == 60:
                    minute = 0
                    if hour == 23:
                        hour = 0
                        charge_schedule.loc[(index - 1), "end_day"] += 1
                    else:
                        hour = hour + 1
                if hour == 24:
                    hour = 0

                charge_schedule.loc[(index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

        # # extracting charging capacity from y variables value.
    charge_schedule_solar = pd.DataFrame(
        columns=['bus_number', 'start_day', 'charging_start_time', 'stop_location', 'end_day',
                 'scenario', 'grid_or_solar', 'charging_end_time'])
    index = 0
    check_time = -1
    number_of_variables = 0
    bus_no = -1

    for i, row in x_y_variables.iterrows():
        if row.variable.split("_")[0] == "y":
            time_1 = row.variable.split("_")[4]
            # print(time_1, check_time)
            if (int(time_1) - int(check_time) >= 1) | (bus_no != row.variable.split("_")[2]):
                charge_schedule_solar.loc[index, "bus_number"] = int(row.variable.split("_")[2])
                charge_schedule_solar.loc[index, "scenario"] = int(row.variable.split("_")[1])
                charge_schedule_solar.loc[index, "grid_or_solar"] = "solar"
                if int(time_1) < 1440:
                    hour = int(row.variable.split("_")[4]) // 60
                    minute = int(row.variable.split("_")[4]) % 60
                    charge_schedule_solar.loc[index, "start_day"] = 1
                elif (int(time_1) >= 1440) and int(time_1) < 2880:
                    hour = int(row.variable.split("_")[4]) // 60 - 24
                    minute = int(row.variable.split("_")[4]) % 60 - 1
                    charge_schedule_solar.loc[index, "start_day"] = 2
                else:
                    hour = int(row.variable.split("_")[4]) // 60 - 48
                    minute = int(row.variable.split("_")[4]) % 60 - 1
                    charge_schedule_solar.loc[index, "start_day"] = 3

                if minute == -1:
                    minute = 59
                    if hour == 0:
                        hour = 23
                        charge_schedule_solar.loc[index, "start_day"] -= 1
                    else:
                        hour = hour - 1
                if hour == 24:
                    hour = 0
                charge_schedule_solar.loc[index, "charging_start_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"
                charge_schedule_solar.loc[index, "stop_location"] = row.variable.split("_")[3]

                # if index == 0:
                #     print(f"Time stamp for index 0 solar = {time_1}")

                # for the last entry update of end time for completion of charging after plug in
                if index != 0:
                    if int(check_time) < 1440:
                        hour = int(check_time) // 60
                        minute = int(check_time) % 60 + 1
                        charge_schedule_solar.loc[(index - 1), "end_day"] = 1
                    elif (int(check_time) >= 1440) and int(check_time) < 2880:
                        hour = int(check_time) // 60 - 24
                        minute = int(check_time) % 60
                        charge_schedule_solar.loc[(index - 1), "end_day"] = 2
                    else:
                        hour = int(check_time) // 60 - 48
                        minute = int(check_time) % 60
                        charge_schedule_solar.loc[(index - 1), "end_day"] = 3

                    if minute == 60:
                        minute = 0
                        if hour == 23:
                            hour = 0
                            charge_schedule_solar.loc[(index - 1), "end_day"] += 1
                        else:
                            hour = hour + 1
                    if hour == 24:
                        hour = 0
                    charge_schedule_solar.loc[
                        (index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

                index += 1

            # updating check time, number of variables and bus number at every iteration
            check_time = time_1
            bus_no = row.variable.split("_")[2]
            # print("bus_no = ", bus_no)
            number_of_variables += 1

            # for the last entry update of end time of dictionary
            if number_of_variables == number_of_y_variables:
                if int(check_time) < 1440:
                    hour = int(check_time) // 60
                    minute = int(check_time) % 60 + 1
                    charge_schedule_solar.loc[(index - 1), "end_day"] = 1
                elif (int(check_time) >= 1440) and int(check_time) < 2880:
                    hour = int(check_time) // 60 - 24
                    minute = int(check_time) % 60
                    charge_schedule_solar.loc[(index - 1), "end_day"] = 2
                else:
                    hour = int(check_time) // 60 - 48
                    minute = int(check_time) % 60
                    charge_schedule_solar.loc[(index - 1), "end_day"] = 3

                if minute == 60:
                    minute = 0
                    if hour == 23:
                        hour = 0
                        charge_schedule_solar.loc[(index - 1), "end_day"] += 1
                    else:
                        hour = hour + 1
                if hour == 24:
                    hour = 0
                charge_schedule_solar.loc[
                    (index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

    # save the charge_schedule as csv
    charge_schedule.to_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/csp_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)
    charge_schedule_solar.to_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/csp_solar_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)
