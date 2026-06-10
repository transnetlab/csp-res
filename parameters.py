import numpy as np
import cplex

# define parameters for the model
Interest_Rate = 0.035  # in fraction
Battery_Years = 12
Grid_Years = 12
Panel_Years = 30
Battery_Amortization_Factor = (Interest_Rate * (1 + Interest_Rate) ** Battery_Years) / (
        (1 + Interest_Rate) ** Battery_Years - 1)
Grid_Amortization_Factor = (Interest_Rate * (1 + Interest_Rate) ** Grid_Years) / ((1 + Interest_Rate) ** Grid_Years - 1)
Panel_Amortization_Factor = (Interest_Rate * (1 + Interest_Rate) ** Panel_Years) / (
        (1 + Interest_Rate) ** Panel_Years - 1)

# print(Battery_Amortization_Factor)
# print(Grid_Amortization_Factor)
# print(Panel_Amortization_Factor)

Euros_to_dollars_exchange_rate = 1.09
Charging_rate = 2.500  # grid to bus (x variables)
Max_battery_capacity = 313 * 0.85
Min_battery_capacity = 313 * 0.15
Solar_battery_charging_rate = 2.500  # battery to bus (y variables)
Solar_energy_price = 0
# NREL website : 300 $
Unit_battery_price = np.asarray([round(500 * Battery_Amortization_Factor / (Euros_to_dollars_exchange_rate * 365), 4)],
                                dtype=np.float64)
Unit_capacity_cost = np.asarray([round(654 * Grid_Amortization_Factor / (Euros_to_dollars_exchange_rate * 365), 4)],
                                dtype=np.float64)
# https://www.nrel.gov/solar/market-research-analysis/solar-installed-system-cost.html
Unit_panel_cost = np.asarray([round((973 * 0.21 * Panel_Amortization_Factor + 16.12 * 25 * 0.21 / 30) / (Euros_to_dollars_exchange_rate * 365), 4)],
                             dtype=np.float64)

# print(Unit_battery_price)
# print(Unit_capacity_cost)
# print(Unit_panel_cost)

Efficiency_solar_panel = 0.2
scale_factor_objective = 1  # scaling the objective coefficients
scale_factor_constraints = 1  # scaling the constraint coefficients
area_scale = 1  # scaling the panel area variables
lower_bound_master_variables = 0
upper_bound_master_variables_grid = cplex.infinity
upper_bound_master_variables = cplex.infinity
upper_bound_master_variables_area = cplex.infinity
depth_of_discharge = 0.90  # depth of discharge
