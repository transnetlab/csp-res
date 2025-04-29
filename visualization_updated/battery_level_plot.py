import pandas as pd
import matplotlib.pyplot as plt
import math


def plot_bess_level(network, folder_path):
    """
    :param network: Network name
    :param folder_path: Path to the folder containing the network
    :return:
    """
    # CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    # folder_path = CURR_DIR[:-22]
    # print(folder_path)
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
        # load battery levels at all locations
        battery_levels_all = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/v_{scenario}_accumulated.csv')
        # print(battery_levels_all)
        # find the maximum bess_energy_level for each location and pick the location with the maximum value
        battery_levels_all_grouped = battery_levels_all.groupby(['location']).agg(
            {'bess_energy_level': 'max'}).reset_index()
        print(battery_levels_all_grouped)
        # find the location with the maximum value
        max_location = battery_levels_all_grouped.loc[battery_levels_all_grouped['bess_energy_level'].idxmax()][
            'location']
        print(max_location)
        # filter the battery_levels_all for the max_location

        if network == 'Durham_2.1k':
            max_location = '93112:1'
        else:
            max_location = 4333

        battery_levels_max_location = battery_levels_all[battery_levels_all['location'] == max_location]
        print(battery_levels_max_location)
        # save the battery_levels_max_location as csv
        battery_levels_max_location.to_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/v_{scenario}_max_location.csv', index=False)
        # arrange in ascending order of time
        battery_levels_max_location = battery_levels_max_location.sort_values(by='time')
        # store the time in a list and the corresponding battery levels in another list
        # time = battery_levels_max_location['time'].tolist()
        # battery_levels = battery_levels_max_location['bess_energy_level'].tolist()
        time, battery_levels = [], []
        for i, row in battery_levels_max_location.iterrows():
            time.append(row.time)
            battery_levels.append(row.bess_energy_level)
            time.append(row.time + 1 / 3)
            battery_levels.append(row.bess_energy_level + row.panel_to_bess)
            time.append(row.time + 2 / 3)
            battery_levels.append(row.bess_energy_level + row.panel_to_bess + row.grid_to_bess)
            row_final = row
        # remove the last two entries from both lists
        # time = time[:-2]
        # battery_levels = battery_levels[:-2]
        time.append(time[-1] + 1 / 3)
        battery_levels.append(row_final.bess_energy_level + row_final.panel_to_bess - row_final.bess_to_bus)
        print(time)
        print(battery_levels)
        # plot the battery levels with respect to time using line plot,
        # if there is an increase using green color,
        # if there is a decrease using red color and if there is no change using blue color
        plt.figure(figsize=(24, 6))
        for i in range(len(time) - 1):
            # print(round(time[i + 1] - math.floor(time[i + 1]), 2))
            if battery_levels[i] < battery_levels[i + 1] and round(time[i + 1] - math.floor(time[i + 1]),
                                                                   2) == 0.33:  # use dark green color
                plt.plot([time[i], time[i + 1]], [battery_levels[i], battery_levels[i + 1]], color='darkgreen')
            elif battery_levels[i] < battery_levels[i + 1] and round(time[i + 1] - math.floor(time[i + 1]), 2) == 0.67:
                plt.plot([time[i], time[i + 1]], [battery_levels[i], battery_levels[i + 1]], color='yellowgreen')
            # elif battery_levels[i] < battery_levels[i + 1] and round(time[i + 1] - math.floor(time[i + 1]), 2) == 0:
            #     print("this case", battery_levels[i], battery_levels[i + 1])
            #     plt.plot([time[i], time[i + 1]], [battery_levels[i], battery_levels[i + 1]], color='b')
            elif battery_levels[i] > battery_levels[i + 1]:
                plt.plot([time[i], time[i + 1]], [battery_levels[i], battery_levels[i + 1]], color='r')
            else:
                plt.plot([time[i], time[i + 1]], [battery_levels[i], battery_levels[i + 1]], color='b')
        # restrict the x-axis from 1020 to 2850
        # plt.xlim(2750, 2900)
        plt.xlabel('Time', fontsize=22)
        plt.ylabel('Battery Level (kWh)', fontsize=22)
        # for green and red color, add the legend
        plt.plot([], 'yellowgreen', label='Grid to BESS')
        plt.plot([], 'darkgreen', label='Panel to BESS')
        plt.plot([], 'r', label='BESS to Bus')
        plt.plot([], 'b', label='Idle')
        # put xticklabels in hours
        # plt.xticks(range(1020, 2880, 120),
        #            ['17', '19', '21', '23', '01', '03', '05', '07', '09', '11', '13', '15', '17', '19', '21', '23'])
        plt.xticks(range(0, 1500, 120), ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '22', '24'])
        if network == 'Durham_2.1k':
            plt.yticks(range(10, 110, 10))
        else:
            plt.yticks(range(50, 400, 50))
        plt.tight_layout()
        # show plot only from 22 and 23
        # plt.xlim(1320, 1440)
        if network == "Durham_2.1k":
            plt.legend(fontsize=18, loc='upper right', bbox_to_anchor=(0.6, 1))
        else:
            plt.legend(fontsize=18, loc='upper right', bbox_to_anchor=(1, 1))
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.savefig(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/bess_battery_level_vs_time_{network}_scenario_{scenario}.pdf',
            dpi=300,
            bbox_inches='tight')
        plt.show()


# import os
#
# CURR_DIR = os.path.dirname(os.path.realpath(__file__))  # current directory
# network = 'Canberra_3.91k'  # change network name here
# folder_path = CURR_DIR[:-22]
# plot_bess_level(network, folder_path)
