import numpy as np

# define parameters for the model
Euros_to_dollars_exchange_rate = 1.09
Charging_rate = 2.500
Max_battery_capacity = 313*0.85
Min_battery_capacity = 313*0.15
Solar_battery_charging_rate = 2.500
Solar_energy_price = 0
# NREL website : 300 $
Unit_battery_price = np.asarray([0.046], dtype=np.float64)
Unit_capacity_cost = np.asarray([0.14], dtype=np.float64)
# https://www.nrel.gov/solar/market-research-analysis/solar-installed-system-cost.html
# NREL website Panels + Inverter +  Electrical System + Structural support+ Maintenance = 1161+400$
Unit_panel_cost = np.asarray([0.017], dtype=np.float64)
Efficiency_solar_panel = 0.2
