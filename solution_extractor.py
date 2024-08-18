# read the .sol file and extract the row and column
import pickle
import pandas as pd
import numpy as np


row_status = pd.DataFrame(columns=['row', 'status'])
column_status = pd.DataFrame(columns=['column', 'status'])

network = 'Canberra_3.91k'
folder_path = f'E:/PycharmProjects/CSP-Benders'
scenarios = 52
temperature = True
benders = True
renewables = True

# open dict_network_name.pkl

with open('./dict_network_name.pkl', 'rb') as f:
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

# concatenate the x_y_variables for scenarios 2, 10, 26, 41, 50
list_scenarios = [4, 10, 26, 33, 41, 50]
# x_y_variables = pd.DataFrame(columns=data_variable.columns)
# for scenario in scenarios:
#     # take data of x and y variables for scenario 1
#     x_y_variables = pd.concat([x_y_variables, data_variable[data_variable['variable'].str.contains(f"x_{scenario}_") | data_variable['variable'].str.contains(f"y_{scenario}_")]])


for scenario in list_scenarios:
    print(scenario)
    # # take data of x and y variables for scenario 1
    x_y_variables = data_variable[data_variable['variable'].str.contains(f"x_{scenario}_") | data_variable['variable'].str.contains(f"y_{scenario}_")]

    # reindex the dataframe
    x_y_variables.reset_index(drop=True, inplace=True)

    # remove variable with value 0
    x_y_variables = x_y_variables[x_y_variables['value'] != 0]
    # find number of x and y variables
    number_of_x_variables = len(x_y_variables[x_y_variables['variable'].str.contains("x")])
    number_of_y_variables = len(x_y_variables[x_y_variables['variable'].str.contains("y")])

    charge_schedule = pd.DataFrame(columns=['bus_number', 'start_day', 'charging_start_time', 'stop_location', 'end_day',
                                            'scenario', 'grid_or_solar', 'charging_end_time'])
    index = 0
    check_time = 0
    number_of_variables = 0
    index_charging_capacity = 0
    index_soc = 0
    bus_no = -1
    for i, row in x_y_variables.iterrows():
        if row.variable.split("_")[0] == 'x':
            # allocating information in variables, with consideration of charging schedule extending to next day
            time = row.variable.split("_")[4]
            if (int(time) - int(check_time) > 1) | (bus_no != row.variable.split("_")[2]):
                charge_schedule.loc[index, "bus_number"] = int(row.variable.split("_")[2])
                charge_schedule.loc[index, "scenario"] = int(row.variable.split("_")[1])
                charge_schedule.loc[index, "grid_or_solar"] = "grid"
                if int(time) <= 1440:
                    hour = int(row.variable.split("_")[4]) // 60
                    minute = int(row.variable.split("_")[4]) % 60 - 1
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

                # for the last entry update of end time for completion of charging after plug in
                if index != 0:
                    if int(check_time) < 1440:
                        hour = int(check_time) // 60
                        minute = int(check_time) % 60
                        charge_schedule.loc[(index - 1), "end_day"] = 1
                    elif (int(check_time) >= 1440) and int(check_time) < 2880:
                        hour = int(check_time) // 60 - 24
                        minute = int(check_time) % 60
                        charge_schedule.loc[(index - 1), "end_day"] = 2
                    else:
                        hour = int(check_time) // 60 - 48
                        minute = int(check_time) % 60
                        charge_schedule.loc[(index - 1), "end_day"] = 3

                    if minute == -1:
                        minute = 59
                        if hour == 0:
                            hour = 23
                            charge_schedule.loc[(index - 1), "end_day"] -= 1
                        else:
                            hour = hour - 1
                    if hour == 24:
                        hour = 0
                    charge_schedule.loc[(index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

                index += 1

            # updating check time, number of variables and bus number at every iteration
            check_time = time
            bus_no = row.variable.split("_")[2]
            number_of_variables += 1

            # for the last entry update of end time of dictionary
            if number_of_variables == number_of_x_variables:
                if int(check_time) < 1440:
                    hour = int(check_time) // 60
                    minute = int(check_time) % 60
                    charge_schedule.loc[(index - 1), "end_day"] = 1
                elif (int(check_time) >= 1440) and int(check_time) < 2880:
                    hour = int(check_time) // 60 - 24
                    minute = int(check_time) % 60
                    charge_schedule.loc[(index - 1), "end_day"] = 2
                else:
                    hour = int(check_time) // 60 - 48
                    minute = int(check_time) % 60
                    charge_schedule.loc[(index - 1), "end_day"] = 3

                if minute == -1:
                    minute = 59
                    if hour == 0:
                        hour = 23
                        charge_schedule.loc[(index - 1), "end_day"] -= 1
                    else:
                        hour = hour - 1
                if hour == 24:
                    hour = 0

                charge_schedule.loc[(index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

        # # extracting charging capacity from y variables value.
    charge_schedule_solar = pd.DataFrame(columns=['bus_number', 'start_day', 'charging_start_time', 'stop_location', 'end_day',
                                                    'scenario', 'grid_or_solar', 'charging_end_time'])
    index = 0
    check_time = 0
    number_of_variables = 0
    bus_no = -1

    for i, row in x_y_variables.iterrows():
        if row.variable.split("_")[0] == "y":
            time_1 = row.variable.split("_")[4]
            if (int(time_1) - int(check_time) > 1) | (bus_no != row.variable.split("_")[2]):
                charge_schedule_solar.loc[index, "bus_number"] = int(row.variable.split("_")[2])
                charge_schedule_solar.loc[index, "scenario"] = int(row.variable.split("_")[1])
                charge_schedule_solar.loc[index, "grid_or_solar"] = "solar"
                if int(time_1) < 1440:
                    hour = int(row.variable.split("_")[4]) // 60
                    minute = int(row.variable.split("_")[4]) % 60 - 1
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

                # for the last entry update of end time for completion of charging after plug in
                if index != 0:
                    if int(check_time) < 1440:
                        hour = int(check_time) // 60
                        minute = int(check_time) % 60
                        charge_schedule_solar.loc[(index - 1), "end_day"] = 1
                    elif (int(check_time) >= 1440) and int(check_time) < 2880:
                        hour = int(check_time) // 60 - 24
                        minute = int(check_time) % 60
                        charge_schedule_solar.loc[(index - 1), "end_day"] = 2
                    else:
                        hour = int(check_time) // 60 - 48
                        minute = int(check_time) % 60
                        charge_schedule_solar.loc[(index - 1), "end_day"] = 3

                    if minute == -1:
                        minute = 59
                        if hour == 0:
                            hour = 23
                            charge_schedule_solar.loc[(index - 1), "end_day"] -= 1
                        else:
                            hour = hour - 1
                    if hour == 24:
                        hour = 0
                    charge_schedule_solar.loc[(index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

                index += 1

            # updating check time, number of variables and bus number at every iteration
            check_time = time_1
            bus_no = row.variable.split("_")[1]
            number_of_variables += 1

            # for the last entry update of end time of dictionary
            if number_of_variables == number_of_y_variables:
                if int(check_time) < 1440:
                    hour = int(check_time) // 60
                    minute = int(check_time) % 60
                    charge_schedule_solar.loc[(index - 1), "end_day"] = 1
                elif (int(check_time) >= 1440) and int(check_time) < 2880:
                    hour = int(check_time) // 60 - 24
                    minute = int(check_time) % 60
                    charge_schedule_solar.loc[(index - 1), "end_day"] = 2
                else:
                    hour = int(check_time) // 60 - 48
                    minute = int(check_time) % 60
                    charge_schedule_solar.loc[(index - 1), "end_day"] = 3

                if minute == -1:
                    minute = 59
                    if hour == 0:
                        hour = 23
                        charge_schedule_solar.loc[(index - 1), "end_day"] -= 1
                    else:
                        hour = hour - 1
                if hour == 24:
                    hour = 0
                charge_schedule_solar.loc[(index - 1), "charging_end_time"] = f"{hour:02d}" + ":" + f"{minute:02d}" + ":00"

    # save the charge_schedule as csv
    charge_schedule.to_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/csp_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)
    charge_schedule_solar.to_csv(
        f'./{network}/{scenarios}_scenario/csp_solar_{dict_network_name[network]}_{scenario}_scenario.csv',
        index=False)
