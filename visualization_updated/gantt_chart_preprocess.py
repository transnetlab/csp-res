import pandas as pd
import os


def preprocess_gantt_chart(network, folder_path):
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

    # create a folder named location if it does not exist
    if not os.path.exists(f'{folder_path}/{network}/{number_of_scenario}_scenario/location'):
        os.makedirs(f'{folder_path}/{network}/{number_of_scenario}_scenario/location')

    for scenario in scenario_list:
        print("Scenario: ", scenario)
        if network == 'Durham_2.1k':
            index_net = 0
        else:
            index_net = 1
        # open v_{scenario}_accumulated.csv
        battery_levels_all = pd.read_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/v_{scenario}_accumulated.csv')
        # find all the unique charging locations
        charging_locations = battery_levels_all['location'].unique()
        print(charging_locations)
        print(len(charging_locations))
        for location in charging_locations:
            print("Location: ", location)
            battery_levels_location = battery_levels_all[battery_levels_all['location'] == location]
            print(battery_levels_location)

            # save the battery_levels_location as csv
            # sort in ascending order of time
            battery_levels_location = battery_levels_location.sort_values(by='time')
            # find the accumulated sum of panel_to_bess and grid_to_bess and create two new columns
            battery_levels_location['panel_to_bess_sum'] = battery_levels_location['panel_to_bess'].cumsum()
            battery_levels_location['grid_to_bess_sum'] = battery_levels_location['grid_to_bess'].cumsum()
            # reset index
            battery_levels_location = battery_levels_location.reset_index(drop=True)
            # replace : in location with a _
            if ':' in str(location):
                name_loc = location.replace(':', '_')
            else:
                name_loc = location
            battery_levels_location.to_csv(
                f'{folder_path}/{network}/{number_of_scenario}_scenario/location/v_scenario_{scenario}_location_{name_loc}.csv',
                index=False)
            print(battery_levels_location)
            # store the time from battery_levels_location in a list
            time_list = battery_levels_location['time'].tolist()
            grid_bus_list = battery_levels_location['grid_to_bus'].tolist()
            grid_bus_extra_list, panel_bus_list = [], []
            grid_bess_used, panel_bess_used = 0, 0
            # find the last time step where the bess_to_bus is not zero and find the time and not the index
            last_positive_time_step = battery_levels_location[battery_levels_location['bess_to_bus'] != 0].index[-1] + 1
            print(last_positive_time_step)
            # find the corresponding time
            last_positive_time = battery_levels_location.loc[last_positive_time_step - 1, 'time']
            print(last_positive_time)
            # sum the grid_to_bess and panel_to_bess values from the last positive time step to the end
            residual_grid_to_bess_prev = battery_levels_location.loc[last_positive_time_step:, 'grid_to_bess'].sum()
            residual_panel_to_bess_prev = battery_levels_location.loc[last_positive_time_step:, 'panel_to_bess'].sum()
            print(residual_grid_to_bess_prev, residual_panel_to_bess_prev)

            lowest_grid = 0
            lowest_solar = 0
            # find the minimum bess_energy_level from battery_levels_location and column bess_energy_level
            min_bess_energy_level = battery_levels_location['bess_energy_level'].min()
            # find the corresponding times and take the max time
            min_times_list = battery_levels_location.loc[
                battery_levels_location['bess_energy_level'] == min_bess_energy_level, 'time']
            min_bess_energy_level_time = min_times_list.max()
            # min_bess_energy_level_time = battery_levels_location.loc[battery_levels_location['bess_energy_level'].idxmin(), 'time']
            print(min_bess_energy_level, min_bess_energy_level_time)
            # find the total bess_to_bus required from the min_bess_energy_level_time to the last_positive_time
            total_bess_to_bus_min = battery_levels_location.loc[
                (battery_levels_location['time'] >= min_bess_energy_level_time) &
                (battery_levels_location['time'] <= last_positive_time),
                'bess_to_bus'].sum()
            print(total_bess_to_bus_min)
            # find the total grid to bess and panel to bess from the min_bess_energy_level_time to the end
            total_grid_to_bess_min = battery_levels_location.loc[
                (battery_levels_location['time'] >= min_bess_energy_level_time) & (
                        battery_levels_location['time'] <= last_positive_time), 'grid_to_bess'].sum()
            total_panel_to_bess_min = battery_levels_location.loc[
                (battery_levels_location['time'] >= min_bess_energy_level_time) & (
                        battery_levels_location['time'] <= last_positive_time), 'panel_to_bess'].sum()

            print(total_grid_to_bess_min, total_panel_to_bess_min)
            residual_grid_to_bess, residual_panel_to_bess = 0, 0
            if total_grid_to_bess_min >= total_bess_to_bus_min:
                residual_grid_to_bess = total_grid_to_bess_min - total_bess_to_bus_min
                residual_panel_to_bess = total_panel_to_bess_min
            else:
                residual_grid_to_bess = 0
                residual_panel_to_bess = total_panel_to_bess_min - (total_bess_to_bus_min - total_grid_to_bess_min)
            residual_grid_to_bess += residual_grid_to_bess_prev
            residual_panel_to_bess += residual_panel_to_bess_prev
            print(residual_grid_to_bess, residual_panel_to_bess)

            for i, row in battery_levels_location.iterrows():
                time_step = row.time
                if time_step <= last_positive_time:
                    cumulative_grid_to_bess = row.grid_to_bess_sum + residual_grid_to_bess - grid_bess_used
                    cumulative_panel_to_bess = row.panel_to_bess_sum + residual_panel_to_bess - panel_bess_used
                    if cumulative_grid_to_bess < 0 and cumulative_grid_to_bess < lowest_grid:
                        # print(time_step, cumulative_grid_to_bess, cumulative_panel_to_bess)
                        lowest_grid = cumulative_grid_to_bess
                    if cumulative_panel_to_bess < 0 and cumulative_panel_to_bess < lowest_solar:
                        # print(time_step, cumulative_grid_to_bess, cumulative_panel_to_bess, grid_bess_used, panel_bess_used)
                        lowest_solar = cumulative_panel_to_bess
                    required_bess_to_bus = row.bess_to_bus
                    if network == "Durham_2.1k" or network == "Canberra_3.91k":
                        # print(time_step, cumulative_grid_to_bess, cumulative_panel_to_bess)
                        # fully from the grid (priority)
                        if cumulative_grid_to_bess >= required_bess_to_bus:
                            grid_bus_extra_list.append(required_bess_to_bus)
                            grid_bess_used += required_bess_to_bus
                            panel_bus_list.append(0)
                            panel_bess_used += 0
                        # both from the grid and the panel (grid priority)
                        elif 0 < cumulative_grid_to_bess < required_bess_to_bus:
                            grid_bus_extra_list.append(cumulative_grid_to_bess)
                            grid_bess_used += cumulative_grid_to_bess
                            panel_bus_list.append(required_bess_to_bus - cumulative_grid_to_bess)
                            panel_bess_used = panel_bess_used + required_bess_to_bus - cumulative_grid_to_bess
                        # fully from the panel
                        else:
                            grid_bus_extra_list.append(0)
                            grid_bess_used += 0
                            panel_bus_list.append(required_bess_to_bus)
                            panel_bess_used += required_bess_to_bus
                    else:
                        # fully from the panel (priority)
                        if cumulative_panel_to_bess >= required_bess_to_bus:
                            panel_bus_list.append(required_bess_to_bus)
                            panel_bess_used += required_bess_to_bus
                            grid_bus_extra_list.append(0)
                            grid_bess_used += 0
                        # both from the panel and the grid (panel priority)
                        elif 0 < cumulative_panel_to_bess < required_bess_to_bus:
                            panel_bus_list.append(cumulative_panel_to_bess)
                            panel_bess_used += cumulative_panel_to_bess
                            grid_bus_extra_list.append(required_bess_to_bus - cumulative_panel_to_bess)
                            grid_bess_used += required_bess_to_bus - cumulative_panel_to_bess
                        # fully from the grid
                        else:
                            panel_bus_list.append(0)
                            panel_bess_used += 0
                            grid_bus_extra_list.append(required_bess_to_bus)
                            grid_bess_used += required_bess_to_bus
                else:
                    grid_bus_extra_list.append(0)
                    panel_bus_list.append(0)

            grid_to_bus_final_list = [grid_bus_list[i] + grid_bus_extra_list[i] for i in range(len(grid_bus_list))]
            print(time_list)
            print(grid_to_bus_final_list)
            print(panel_bus_list)
            print(len(time_list), len(grid_to_bus_final_list), len(panel_bus_list))
            print(sum(grid_to_bus_final_list), sum(panel_bus_list))
            print(grid_bess_used)
            print(panel_bess_used)

            # plot a line plot with time on x-axis and grid_to_bus_final_list on y-axis and panel_bus_list on top of grid_to_bus_final_list
            # use grid_to_bus_final value as the base for panel_bus_list
            total_list = [grid_to_bus_final_list[i] + panel_bus_list[i] for i in range(len(time_list))]
            # find the first and last time step where the total_list entry is not zero
            first_non_zero_time_step = total_list.index(next(filter(lambda x: x != 0, total_list)))
            last_non_zero_time_step = len(total_list) - total_list[::-1].index(
                next(filter(lambda x: x != 0, total_list[::-1])))
            print(first_non_zero_time_step, last_non_zero_time_step)
            dummy_list = [0 for i in range(first_non_zero_time_step + 1, last_non_zero_time_step - 1)]
            dummy_time_list = [time_list[i] for i in range(first_non_zero_time_step + 1, last_non_zero_time_step - 1)]
            # change time_list to an np array
            df_grid_panel_bus = pd.DataFrame(
                {'time': time_list, 'solar': panel_bus_list, 'grid': grid_to_bus_final_list})
            print(lowest_grid)
            print(lowest_solar)
            # create two columns with actual_grid_to_bess and actual_panel_to_bess
            battery_levels_location['actual_grid_to_bess_to_bus'] = grid_bus_extra_list
            battery_levels_location['actual_panel_to_bess_to_bus'] = panel_bus_list
            battery_levels_location.to_csv(
                f'{folder_path}/{network}/{number_of_scenario}_scenario/location/v_scenario_{scenario}_location_{name_loc}.csv',
                index=False)
            print(charging_locations)

    # open all the csv files in the location folder and combine them in a dataframe

    for scenario in scenario_list:
        df_merged = pd.DataFrame()
        for file in os.listdir(f'{folder_path}/{network}/{number_of_scenario}_scenario/location'):
            # if file name starts with v_scenario_{scenario}
            if file.startswith(f'v_scenario_{scenario}'):
                df = pd.read_csv(f'{folder_path}/{network}/{number_of_scenario}_scenario/location/{file}')
                df_merged = pd.concat([df_merged, df])
        # filter only the rows where bess_to_bus is not zero
        df_merged = df_merged[df_merged['bess_to_bus'] != 0]
        print(df_merged)
        # find the sum of bess_to_bus column
        sum_bess_to_bus = df_merged['bess_to_bus'].sum()
        print(sum_bess_to_bus)
        sum_actual_grid_to_bess = df_merged['actual_grid_to_bess_to_bus'].sum()
        sum_actual_panel_to_bess = df_merged['actual_panel_to_bess_to_bus'].sum()
        print(sum_actual_grid_to_bess, sum_actual_panel_to_bess)
        # save the df_merged as csv
        df_merged.to_csv(
            f'{folder_path}/{network}/{number_of_scenario}_scenario/v_scenario_{scenario}_location_all.csv',
            index=False)
