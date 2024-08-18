import pandas as pd

# create a csv file with columns run_id, network, scenario, benders_cut, benders_strategy, variable_type, parallel_mode, temperature, renewable
run_file = pd.DataFrame(columns=['Run_ID', 'Network_Name', 'Benders_strategy', 'Apply_Benders_Cut', 'Scenarios', 'Variable_Type',
                                 'Parallel_Mode', 'Use_Temperature', 'Use_Renewables', ])
# start the run_id from 1 for Canberra_3.91k
run_file.loc[0] = [1, 'Canberra_3.91k', 1, True, 1, 'C', 0, True, True]
run_file.loc[1] = [2, 'Canberra_3.91k', 1, False, 1, 'C', 0, True, True]
run_file.loc[2] = [3, 'Canberra_3.91k', 1, True, 3, 'C', 0, True, True]
run_file.loc[3] = [4, 'Canberra_3.91k', 1, False, 3, 'C', 0, True, True]
run_file.loc[4] = [5, 'Canberra_3.91k', 1, True, 12, 'C', 0, True, True]
run_file.loc[5] = [6, 'Canberra_3.91k', 1, False, 12, 'C', 0, True, True]
run_file.loc[6] = [7, 'Canberra_3.91k', 1, True, 52, 'C', 0, True, True]
run_file.loc[7] = [8, 'Canberra_3.91k', 1, False, 52, 'C', 0, True, True]
run_file.loc[8] = [9, 'Canberra_3.91k', 1, True, 52, 'C', 0, False, True]
run_file.loc[9] = [10, 'Canberra_3.91k', 1, True, 52, 'C', 0, True, False]
run_file.loc[10] = [11, 'Canberra_3.91k', 1, True, 52, 'C', 0, False, False]

# continue the run_id from 12 for Thunder_bay_903
run_file.loc[11] = [12, 'Thunder_bay_903', 1, True, 1, 'C', 0, True, True]
run_file.loc[12] = [13, 'Thunder_bay_903', 1, False, 1, 'C', 0, True, True]
run_file.loc[13] = [14, 'Thunder_bay_903', 1, True, 3, 'C', 0, True, True]
run_file.loc[14] = [15, 'Thunder_bay_903', 1, False, 3, 'C', 0, True, True]
run_file.loc[15] = [16, 'Thunder_bay_903', 1, True, 12, 'C', 0, True, True]
run_file.loc[16] = [17, 'Thunder_bay_903', 1, False, 12, 'C', 0, True, True]
run_file.loc[17] = [18, 'Thunder_bay_903', 1, True, 52, 'C', 0, True, True]
run_file.loc[18] = [19, 'Thunder_bay_903', 1, False, 52, 'C', 0, True, True]
run_file.loc[19] = [20, 'Thunder_bay_903', 1, True, 52, 'C', 0, False, True]
run_file.loc[20] = [21, 'Thunder_bay_903', 1, True, 52, 'C', 0, True, False]
run_file.loc[21] = [22, 'Thunder_bay_903', 1, True, 52, 'C', 0, False, False]

# continue the run_id from 23 for Durham_2.1k
run_file.loc[22] = [23, 'Durham_2.1k', 1, True, 1, 'C', 0, True, True]
run_file.loc[23] = [24, 'Durham_2.1k', 1, False, 1, 'C', 0, True, True]
run_file.loc[24] = [25, 'Durham_2.1k', 1, True, 3, 'C', 0, True, True]
run_file.loc[25] = [26, 'Durham_2.1k', 1, False, 3, 'C', 0, True, True]
run_file.loc[26] = [27, 'Durham_2.1k', 1, True, 12, 'C', 0, True, True]
run_file.loc[27] = [28, 'Durham_2.1k', 1, False, 12, 'C', 0, True, True]
run_file.loc[28] = [29, 'Durham_2.1k', 1, True, 52, 'C', 0, True, True]
run_file.loc[29] = [30, 'Durham_2.1k', 1, False, 52, 'C', 0, True, True]
run_file.loc[30] = [31, 'Durham_2.1k', 1, True, 52, 'C', 0, False, True]
run_file.loc[31] = [32, 'Durham_2.1k', 1, True, 52, 'C', 0, True, False]
run_file.loc[32] = [33, 'Durham_2.1k', 1, True, 52, 'C', 0, False, False]

# continue the run_id from 34 for Thunder_bay_clustering
run_file.loc[33] = [34, 'Thunder_bay_clustering', 1, True, 1, 'C', 0, True, True]
run_file.loc[34] = [35, 'Thunder_bay_clustering', 1, True, 2, 'C', 0, True, True]
run_file.loc[35] = [36, 'Thunder_bay_clustering', 1, True, 4, 'C', 0, True, True]
run_file.loc[36] = [37, 'Thunder_bay_clustering', 1, True, 13, 'C', 0, True, True]
run_file.loc[37] = [38, 'Thunder_bay_clustering', 1, True, 26, 'C', 0, True, True]
run_file.loc[38] = [39, 'Thunder_bay_clustering', 1, True, 52, 'C', 0, True, True]
run_file.loc[39] = [40, 'Thunder_bay_clustering', 1, False, 1, 'C', 0, True, True]
run_file.loc[40] = [41, 'Thunder_bay_clustering', 1, False, 2, 'C', 0, True, True]
run_file.loc[41] = [42, 'Thunder_bay_clustering', 1, False, 4, 'C', 0, True, True]
run_file.loc[42] = [43, 'Thunder_bay_clustering', 1, False, 13, 'C', 0, True, True]
run_file.loc[43] = [44, 'Thunder_bay_clustering', 1, False, 26, 'C', 0, True, True]
run_file.loc[44] = [45, 'Thunder_bay_clustering', 1, False, 52, 'C', 0, True, True]


run_file.to_csv('run_file.csv', index=False)

# # make log file to store the output
# log_file = pd.DataFrame(columns=['Run_ID', 'Time_Stamp', 'Network_Name',
#                                  'Scenarios', 'Objective_Value in $',
#                                  'Run_Time in minutes', 'Build_Time in minutes',
#                                  'Variables in millions', 'Constraints in millions',
#                                  'Status', 'Apply_Benders_Cut', 'Use_Temperature', 'Use_Renewables',
#                                  'Solar_Panel_Cost', 'Battery_Storage_Cost', 'Grid_Capacity_Cost'])
# log_file.to_csv('log_file.csv', index=False)

# # open dict_network_name.pkl file and store the network names
# import pickle
# with open('./dict_network_name.pkl', 'rb') as f:
#     dict_network_name = pickle.load(f)
#
# dict_network_name['Durham_2.1k'] = 'durham'
#
# # save the updated dictionary
# with open('./dict_network_name.pkl', 'wb') as f:
#     pickle.dump(dict_network_name, f)