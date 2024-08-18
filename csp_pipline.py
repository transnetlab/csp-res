from input_file import run_input_file
from csp import build_and_solve_scenario_based_csp
from data_preprocessing import preprocessing
from scenario_builder import build_scenario
import sys

"""
Flow of the code:
------------------
input_file.py and parameters.py (set the network details and other parameters using run_id from run_file.csv)
||__ preprocessing (csp_pipline.py -> data_preprocessing.py)
            |__ assign_bus_number
            |__ calculate_time_stamps_and_charging_opportunity
            |__ estimate_charging_opportunity_wise_energy_requirement
            |__ find_time_stamp_grid
|__ build_scenario (scenario_builder.py)
|__ build_and_solve_scenario_based_csp (csp.py)
    |__ add_first_stage_variables
    |__ add_decision_variables_and_bus_energy_level_constraints
    |__ add_grid_capacity_constraints
    |__ add_solar_battery_level_and_max_energy_level_constraints           
"""

# take arguments just after python3 csp_pipline.py run_id
try:
    run_id = int(sys.argv[1])
except ValueError:
    # take input from the user
    run_id = int(input("Enter the run_id: "))
# run the input file
kwargs_preprocessing, kwargs_csp = run_input_file(run_id)

# data processing step
(dict_time_stamp, dict_charging_opportunity_time_stamp, dict_energy_required,
 end_time_stamp, charging_locations, dict_time_stamp_grid, start_time_stamp) = preprocessing(**kwargs_preprocessing)

# scenario builder with renewable or without renewable
if kwargs_csp['use_renewables']:
    dict_scenario_wise_gti = build_scenario(kwargs_preprocessing['network_name'], kwargs_preprocessing['scenarios'])
else:
    dict_scenario_wise_gti = {}

#############################################################################################################
# csp_optimisation_scenario
csp_scenario_model, dict_scenario_solution = build_and_solve_scenario_based_csp(dict_charging_opportunity_time_stamp,
                                                                                dict_scenario_wise_gti,
                                                                                dict_energy_required,
                                                                                charging_locations,
                                                                                end_time_stamp,
                                                                                dict_time_stamp_grid,
                                                                                start_time_stamp,
                                                                                **kwargs_csp)
