"""
Main code for post-processing and visualization of the results of the optimization model.
"""
import os
from bus_stop import run_bus_stops
from buses_energy_variation import run_buses_energy_variations_plots
from gti_temperature_variations import run_gti_temp_variations
from scenario_wise_master_variables_analysis import analyze_master_variables
from results_analysis import analyze_benders_results
from solution_extractor import extract_solution
from solar_to_grid_postprocess import postprocess_solar_to_grid
from battery_level_plot import plot_bess_level
from scenario_location_energy_plot import plot_scenario_location_energy
from gantt_chart_preprocess import preprocess_gantt_chart
from gantt_chart_intermediate import run_intermediate_gantt_chart_data
from grid_solar_mapping import map_grid_or_solar_gantt_chart
from gantt_chart import plot_gantt_chart

CURR_DIR = os.path.dirname(os.path.realpath(__file__))  # current directory
network = 'Durham_2.1k'  # change network name here
folder_path = CURR_DIR[:-22]
run_bus_stops(network, folder_path)
run_buses_energy_variations_plots(network, folder_path)
run_gti_temp_variations(network, folder_path)
analyze_master_variables(network, folder_path)
analyze_benders_results(network, folder_path)
extract_solution(network, folder_path)
postprocess_solar_to_grid(network, folder_path)
plot_bess_level(network, folder_path)
plot_scenario_location_energy(network, folder_path)
preprocess_gantt_chart(network, folder_path)
run_intermediate_gantt_chart_data(network, folder_path)
map_grid_or_solar_gantt_chart(network, folder_path)
plot_gantt_chart(network, folder_path)
