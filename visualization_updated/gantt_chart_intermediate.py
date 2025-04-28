import pandas as pd


def run_intermediate_gantt_chart_data(network, folder_path):
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
    for scenario in scenario_list:
        # open y_{scenario}_accumulated.csv
        bess_to_bus_df = pd.read_csv(
            f"{folder_path}/{network}/{number_of_scenario}_scenario/y_{scenario}_accumulated.csv")
        grid_solar_to_bus_df = pd.read_csv(
            f"{folder_path}/{network}/{number_of_scenario}_scenario/v_scenario_{scenario}_location_all.csv")
        print(bess_to_bus_df)
        print(grid_solar_to_bus_df)
        # create a new column in bess_to_bus_df called 'grid/solar'
        bess_to_bus_df['grid/solar'] = 0
        grid_solar_to_bus_df['variable_name'] = grid_solar_to_bus_df['variable_name'].astype(
            str)  # Ensure column is string type
        grid_solar_to_bus_df['actual_location'] = grid_solar_to_bus_df['variable_name'].apply(lambda x: x.split("_")[2])
        bess_to_bus_df['actual_location'] = bess_to_bus_df['variable_name'].apply(lambda x: x.split("_")[3])
        # save
        grid_solar_to_bus_df.to_csv(
            f"{folder_path}/{network}/{number_of_scenario}_scenario/v_scenario_{scenario}_location_all.csv",
            index=False)
        print(bess_to_bus_df)
        for i, row in grid_solar_to_bus_df.iterrows():
            location = row.actual_location
            time = row.time
            grid_to_bess_to_bus_value = row.actual_grid_to_bess_to_bus
            panel_to_bess_to_bus_value = row.actual_panel_to_bess_to_bus
            # find the corresponding time and location in grid_solar_to_bus_df
            grid_to_bus_used = 0
            solar_to_bus_used = 0
            next_time = time + 1
            if next_time == 1440:
                next_time = 0
            df_filtered_bess_to_bus = bess_to_bus_df[
                (bess_to_bus_df['actual_location'] == location) & (bess_to_bus_df['time'] == next_time)]
            for j, row_bess in df_filtered_bess_to_bus.iterrows():
                residual_grid = grid_to_bess_to_bus_value - grid_to_bus_used
                residual_solar = panel_to_bess_to_bus_value - solar_to_bus_used
                bess_to_bus_value = row_bess.value
                if bess_to_bus_value <= residual_grid:
                    bess_to_bus_df.at[j, 'grid/solar'] = 'grid'
                    grid_to_bus_used += bess_to_bus_value
                elif bess_to_bus_value <= residual_solar and bess_to_bus_value > residual_grid:
                    bess_to_bus_df.at[j, 'grid/solar'] = 'solar'
                    solar_to_bus_used += bess_to_bus_value
                else:
                    bess_to_bus_df.at[j, 'grid/solar'] = 'both'
                    grid_to_bus_used += residual_grid
                    solar_to_bus_used += bess_to_bus_value - residual_grid
        print(bess_to_bus_df)
        # save the updated bess_to_bus_df
        bess_to_bus_df.to_csv(f"{folder_path}/{network}/{number_of_scenario}_scenario/y_{scenario}_grid_or_solar.csv",
                              index=False)
