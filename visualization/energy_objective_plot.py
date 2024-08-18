# read the .sol file and extract the row and column
import matplotlib.pyplot as plt
import pandas as pd
from tou_pricing import tou_pricing_time_stamp_wise
import parameters
import pickle

network = 'Durham_2.1k'
scenarios = 52
temperature = True
renewables = False
folder_path = f'E:/PycharmProjects/CSP-Benders'

# open the file
with open('./dict_network_name.pkl', 'rb') as f:
    dict_network_short_name = pickle.load(f)

if temperature:
    data = pd.read_csv(
        f'{folder_path}/{network}/{scenarios}_scenario/csp_{dict_network_short_name[network]}_{scenarios}_benders_True_'
        f'temperature_{temperature}_renewables_{renewables}.sol', delimiter="=")
else:
    data = pd.read_csv(f'{folder_path}/{network}/without_temperature/1_scenario/csp_'
                       f'{dict_network_short_name[network]}_{scenarios}_'
                       f'scenarios_benders_True_temperature_{temperature}_renewables_{renewables}.sol', delimiter="=")
data = data[24:-5]
# data column names
data.columns = ['type', 'name', 'index', 'slack']

# remove the last 6 letters from each row in name column
data['name'] = data['name'].str[:-6]

# if type starts with '<variable' then in column_status dataframe
data_variable = data[data['type'].str.contains('<variable name')]

# child variables
data_grid = data_variable[data_variable['name'].str.contains("x")]
data_grid.loc[:, 'value'] = data_grid.loc[:, 'slack'].str[:-2].copy()
data_solar = data_variable[data_variable.loc[:, 'name'].str.contains("y")]
data_solar.loc[:, 'value'] = data_solar.loc[:, 'slack'].str[:-2].copy()
# find the location of decision variables
data_grid.loc[:, 'location'] = data_grid.loc[:, 'name'].str.split("_").str[3]
data_solar.loc[:, 'location'] = data_solar.loc[:, 'name'].str.split("_").str[3]


# master variables
data_master_grid = data_variable[data_variable['name'].str.contains("z")]
data_master_grid.loc[:, 'value'] = data_master_grid.loc[:, 'slack'].str[:-2].copy()
data_master_solar = data_variable[data_variable['name'].str.contains("a")]
data_master_solar.loc[:, 'value'] = data_master_solar.loc[:, 'slack'].str[:-2].copy()
data_master_battery = data_variable[data_variable['name'].str.contains("s")]
data_master_battery.loc[:, 'value'] = data_master_battery.loc[:, 'slack'].str[:-2].copy()

# find location
data_master_grid.loc[:, 'location'] = data_master_grid.loc[:, 'name'].str.split("_").str[1]
data_master_solar.loc[:, 'location'] = data_master_solar.loc[:, 'name'].str.split("_").str[1]
data_master_battery.loc[:, 'location'] = data_master_battery.loc[:, 'name'].str.split("_").str[1]

# find the scenario
data_grid.loc[:, 'status'] = data_grid.loc[:, 'name'].str.split("_").str[1]
data_solar.loc[:, 'status'] = data_solar.loc[:, 'name'].str.split("_").str[1]

# convert str to float in value column
data_grid.loc[:, 'value'] = data_grid.loc[:, 'value'].astype(float)
data_solar.loc[:, 'value'] = data_solar.loc[:, 'value'].astype(float)

# find the sum of value corresponding to each status by using group_by
data_grid_grouped = data_grid.groupby(['status']).agg({'value': 'sum'}).reset_index()
data_solar_grouped = data_solar.groupby(['status']).agg({'value': 'sum'}).reset_index()

# data_solar_grouped.to_csv(f'./{network}/solar_status_{dict_network_short_name[network]}_{number_of_scenario}_scenarios_145_buses_.csv', index=False)
# data_grid_grouped.to_csv(f'./{network}/grid_status_{dict_network_short_name[network]}_{number_of_scenario}_scenarios_145_buses_.csv', index=False)

# convert the status to int
data_grid_grouped['status'] = data_grid_grouped['status'].astype(int)
data_solar_grouped['status'] = data_solar_grouped['status'].astype(int)

# sort the data grid and data solar grouped by status
data_grid_grouped = data_grid_grouped.sort_values(by=['status'])
data_solar_grouped = data_solar_grouped.sort_values(by=['status'])

# plot the bar graph for grid and solar values
# figure size
plt.figure(figsize=(12, 6))
# for week wise

if renewables:
    plt.bar(data_solar_grouped['status'], data_solar_grouped['value'], color='green', label='Solar Powered', alpha=0.5,
            bottom=data_grid_grouped['value'])
    plt.bar(data_grid_grouped['status'], data_grid_grouped['value'], color='red', label='Grid Powered', alpha=0.5)
else:
    plt.bar(data_grid_grouped['status'], data_grid_grouped['value'], color='red', label='Grid Powered', alpha=0.5)

plt.xlabel('Week of the year', fontsize=20)
plt.ylabel('Energy (kWh)', fontsize=20)
# increase the font size of legend
plt.legend()
plt.legend(fontsize=16)
# set xticks and yticks font size
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
# save the plot
# plt.savefig(f'{folder_path}/{network}/visualization/energy_required_{network}.pdf', bbox_inches='tight')
plt.show()
#
Total_energy = (data_grid_grouped['value'].sum() + data_solar_grouped['value'].sum())/1000
print(f"Total energy: {Total_energy} MWh")
# # evaluate the objective value for each scenario
# data_grid['time_stamp'] = data_grid['name'].str.split("_").str[4]
# # convert the time_stamp to int
# data_grid['time_stamp'] = data_grid['time_stamp'].astype(int)
# # apply the check_time_period function to the time_stamp column and status column
# # data_grid['time_period'] = data_grid.apply(
# #     lambda x: check_time_period(x['time_stamp'], x['status'], number_of_scenarios=scenarios, network=network), axis=1)
# for index, row in data_grid.iterrows():
#     data_grid.loc[index, 'time_period'] = tou_pricing_time_stamp_wise(row['time_stamp'],
#                                                                       int(row['status']), scenarios, network)
#
# # multiply the value with the time_period
# data_grid['value_'] = data_grid['value'] * data_grid['time_period'] * 1.09
#
# # group by scenario and sum the value
# data_grid_grouped = data_grid.groupby(['status']).agg({'value_': 'sum'}).reset_index()
#
# # for solar objective value multiply the value with the solar energy price
# data_solar['value_'] = data_solar['value'] * parameters.Solar_energy_price * 1.09
# # group by scenario and sum the value
# data_solar_grouped = data_solar.groupby(['status']).agg({'value_': 'sum'}).reset_index()
#
# # plt the bar graph for objective value
# # figure size
# plt.figure(figsize=(12, 6))
# # for week wise
# # number_of_scenario = 52
# # convert the status to int
# data_grid_grouped['status'] = data_grid_grouped['status'].astype(int)
# data_solar_grouped['status'] = data_solar_grouped['status'].astype(int)
# # sort the data grid and data solar grouped by status
# data_grid_grouped.sort_values(by=['status'], inplace=True)
# data_solar_grouped = data_solar_grouped.sort_values(by=['status'])
# # plot the bar graph for grid and solar values
# if renewables:
#     plt.bar(data_grid_grouped['status'], data_grid_grouped['value_'], color='red', label='Grid Powered', alpha=0.5)
#     plt.bar(data_solar_grouped['status'], data_solar_grouped['value_'], color='green', label='Solar Powered', alpha=0.5,
#             bottom=data_grid_grouped['value_'])
# else:
#     plt.bar(data_grid_grouped['status'], data_grid_grouped['value_'], color='red', label='Grid Powered', alpha=0.5)
#
# plt.xlabel('Week of the year', fontsize=20)
# # objective value in euros
# plt.ylabel('Objective Value ($)', fontsize=20)
# # increase the font size of legend
# plt.legend()
# plt.legend(fontsize=16)
# # set xticks and yticks font size
# plt.xticks(fontsize=16)
# plt.yticks(fontsize=16)
#
# # save the plot
# # plt.savefig(f'{folder_path}/{network}/visualization/objective_value_{network}.pdf', bbox_inches='tight')
# plt.show()
#
# # cost analysis
# grid_cost = data_grid_grouped['value_'].sum()
# solar_cost = data_solar_grouped['value_'].sum()
# total_cost = grid_cost + solar_cost
# print(f"Grid cost: {grid_cost/scenarios}")
# print(f"Solar cost: {solar_cost/scenarios}")
# print(f"Total cost: {total_cost/scenarios}")
