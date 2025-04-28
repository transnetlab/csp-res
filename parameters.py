import numpy as np
import cplex

# define parameters for the model
Euros_to_dollars_exchange_rate = 1.09
Charging_rate = 2.500  # grid to bus (x variables)
Max_battery_capacity = 313 * 0.85
Min_battery_capacity = 313 * 0.15
Solar_battery_charging_rate = 2.500  # battery to bus (y variables)
Solar_energy_price = 0
# NREL website : 300 $
Unit_battery_price = np.asarray([0.1047], dtype=np.float64)
Unit_capacity_cost = np.asarray([0.1370], dtype=np.float64)
# https://www.nrel.gov/solar/market-research-analysis/solar-installed-system-cost.html
Unit_panel_cost = np.asarray([0.0256], dtype=np.float64)
Efficiency_solar_panel = 0.2
scale_factor_objective = 1  # scaling the objective coefficients
scale_factor_constraints = 1  # scaling the constraint coefficients
area_scale = 1  # scaling the panel area variables
lower_bound_master_variables = 0
upper_bound_master_variables_grid = cplex.infinity
upper_bound_master_variables = cplex.infinity
upper_bound_master_variables_area = cplex.infinity
depth_of_discharge = 0.90  # depth of discharge
