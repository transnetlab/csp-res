# import sys
import time
import numpy as np
import pandas as pd
import cplex
from tqdm import tqdm
import parameters
from tou_pricing import tou_pricing_time_stamp_wise, which_hour
from stability_test_lp import scale_model, update_model


# sys.path.append(r"c:\program files\ibm\ilog\cplex_studio2211\cplex\python\3.10\x64_win64")


def add_first_stage_variables(model,
                              charging_locations,
                              variable_type,
                              benders_annotation,
                              object_type,
                              bender=False,
                              renewable=True):
    """
    creates the first stage variables for the model
    :param model:  cplex model
    :param charging_locations: list of charging locations
    :param variable_type: type of variable continuous or Integer
    :param benders_annotation: annotation for benders cut
    :param object_type: type of variable for benders cut
    :param bender: boolean value to add benders cut or not
    :param renewable: renewable energy integration considered or not
    :return:
    model: cplex model
    """
    # storing the index of the variables in the dict with variable name as key
    dict_master_variables_index = {}

    # adding first stage variables for each variable
    for location in tqdm(charging_locations, desc="Adding first stage variables"):

        # if renewable energy integration is considered adding solar and battery capacity variables
        if renewable:

            # variable names
            grid_capacity_variable = "z" + "_" + str(location)
            area_string = "a" + "_" + str(location)
            battery_capacity = "s" + "_" + str(location)

            index_grid = \
                list(model.variables.add(obj=parameters.Unit_capacity_cost * parameters.scale_factor_objective,
                                         names=[grid_capacity_variable], lb=[parameters.lower_bound_master_variables],
                                         ub=[parameters.upper_bound_master_variables_grid],
                                         types=[variable_type]))[0]
            index_area = list(
                model.variables.add(
                    obj=parameters.Unit_panel_cost * parameters.scale_factor_objective * parameters.area_scale,
                    names=[area_string],
                    lb=[parameters.lower_bound_master_variables], ub=[parameters.upper_bound_master_variables_area],
                    types=[variable_type]))[0]
            index_battery = \
                list(model.variables.add(obj=parameters.Unit_battery_price * parameters.scale_factor_objective,
                                         names=[battery_capacity], lb=[parameters.lower_bound_master_variables],
                                         ub=[parameters.upper_bound_master_variables],
                                         types=[variable_type]))[0]

            # storing the index of the variables in the dict_master_variables_index
            dict_master_variables_index[grid_capacity_variable] = index_grid
            dict_master_variables_index[area_string] = index_area
            dict_master_variables_index[battery_capacity] = index_battery

            # adding annotation for benders cut
            if bender:
                model.long_annotations.set_values(benders_annotation, object_type,
                                                  [(index_grid, 0), (index_area, 0), (index_battery, 0)])

        # if no renewables then only grid capacity variable
        else:

            # variable name
            grid_capacity_variable = "z" + "_" + str(location)

            index_grid = \
                list(model.variables.add(obj=parameters.Unit_capacity_cost * parameters.scale_factor_objective,
                                         names=[grid_capacity_variable], lb=[parameters.lower_bound_master_variables],
                                         ub=[parameters.upper_bound_master_variables_grid],
                                         types=[variable_type]))[0]

            # storing the index of the variables in the dict_master_variables_index
            dict_master_variables_index[grid_capacity_variable] = index_grid

            # adding annotation for benders cut
            if bender:
                model.long_annotations.set_values(benders_annotation, object_type, [(index_grid, 0)])

    # return the model and dict_master_variables_index
    return model, dict_master_variables_index


def add_decision_variables_and_bus_energy_level_constraints(model,
                                                            scenarios: int,
                                                            dict_charging_event: dict,
                                                            dict_energy: dict,
                                                            dict_grid: dict,
                                                            bender: bool,
                                                            benders_annotation,
                                                            object_type,
                                                            network: str,
                                                            bus_list_overall,
                                                            probability=1 / 3,
                                                            renewable=True):
    """
    This function adds decision variables for the model and energy constraints
    :param model: cplex model
    :param scenarios: number of scenarios
    :param dict_charging_event: dictionary of bus number and charging event wise time stamp
    :param dict_energy: dictionary of energy required for each charging event
    :param dict_grid: dictionary of timestamp wise buses available at grid
    :param bender: boolean value to add benders cut or not
    :param benders_annotation: annotation for benders cut
    :param object_type: type of variable for benders cut
    :param network: name of the network
    :param bus_list_overall: list of total buses available
    :param probability: probability of the scenario
    :param renewable: renewable energy integration considered or not
    :return:
    model: cplex model
    dict_grid_index: Indices corresponding to the grid to bus variables
    dict_solar_index: Indices corresponding to the BESS to bus variables
    """

    # initializing the dict_grid_index and dict_solar_index to store index of buses
    # charging variables present at that time stamp
    dict_grid_index = {}
    dict_solar_index = {}

    # for each scenario
    for scenario in range(1, scenarios + 1):
        dict_grid_index[scenario] = {}
        dict_solar_index[scenario] = {}

        # for each time stamp the buses are available at the grid
        for keys, v in dict_grid[scenario].items():
            dict_grid_index[scenario][keys] = {}
            dict_solar_index[scenario][keys] = {}

            # for each bus available at the grid
            for value_key in v.keys():
                dict_grid_index[scenario][keys][value_key] = []
                dict_solar_index[scenario][keys][value_key] = []

    # add bus-specific initial energy level variables across scenarios (same master variable)
    # for all the buses in bus_overall_list
    # bus_battery_start = {}
    # for bus in bus_list_overall:
    #     constant_energy_bus = "q" + "_" + str(bus)
    #     index_energy_bus_init = list(
    #         model.variables.add(names=[constant_energy_bus], lb=[parameters.lower_bound_master_variables],
    #                             ub=[parameters.Max_battery_capacity],
    #                             types=["C"]))[0]
    #     bus_battery_start[bus] = index_energy_bus_init
    #
    #     # adding annotation if benders cut is applied
    #     if bender:
    #         model.long_annotations.set_values(benders_annotation, object_type, index_energy_bus_init, 0)

    index_scenario_bus = {}
    # iterating over the scenarios
    for scenario in tqdm(range(1, scenarios + 1), desc="Adding scenarios wise decision variables and allowed "
                                                       "transfer from grid or solar-powered battery"):

        # iterating over the buses
        index_scenario_bus[scenario] = {}
        for bus, time_stamps_for_charging_opportunity in dict_charging_event[scenario].items():

            # for tracking energy level at the previous charging event
            previous_charging_event_stamp_index = int()
            index_energy = int()

            # for tracking the last charging event and initializing the last index energy
            last_charging_event = list(time_stamps_for_charging_opportunity.keys())[-1]
            last_index_energy = int()

            # iterating over all the charging events
            for charging_opportunity, time_stamps in time_stamps_for_charging_opportunity.items():

                # adding constraints for the charging event only if any opportunity exists
                if len(time_stamps) > 1:
                    #############################################################################################
                    # storing index and coefficient in the following list
                    list_index_energy = []
                    list_coefficient_energy = []
                    #############################################################################################

                    # iterating over the time stamp for the charging event
                    for index, time_stamp in enumerate(time_stamps[:-1]):

                        # location is stored in the last index of the time_stamps
                        location = time_stamps[-1]

                        # energy from grid x_{bjt}^{w}
                        x_variable = ("x" + "_" + str(scenario) + "_" + str(bus) + "_" +
                                      str(location) + "_" + str(time_stamp))

                        # coefficient for the x variable will be the price of the energy at that time stamp
                        # and the probability of the scenario
                        objective_coefficient = np.asarray([tou_pricing_time_stamp_wise(time_stamp,
                                                                                        scenario, scenarios,
                                                                                        network) * parameters.scale_factor_objective],
                                                           dtype=np.float64) * probability

                        # adding the x variable to the model
                        index_x = model.variables.add(obj=objective_coefficient, names=[x_variable], types=["C"],
                                                      lb=[0],
                                                      ub=[parameters.Charging_rate])
                        # print(scenario, bus, location, time_stamp)
                        # print(index_x)
                        # print(list(index_x))
                        # print(list(index_x)[0])
                        #################################################################################
                        # adding index of the buses available at the depot for charging
                        # at that time stamp to grid and solar dict
                        dict_grid_index[scenario][time_stamp][location].append(list(index_x)[0])

                        # adding annotation if benders cut is applied
                        if bender:
                            model.long_annotations.set_values(benders_annotation, object_type, list(index_x)[0],
                                                              scenario)

                        # adding index and coefficient for the x and y variable for that charging opportunity/event
                        list_index_energy.append(list(index_x)[0])
                        list_coefficient_energy.append(-1 * parameters.scale_factor_constraints)
                        #################################################################################

                        # adding y variables only if renewables are considered
                        if renewable:

                            # energy from solar-powered battery y_{bjt}^{w}
                            y_variable = ("y" + "_" + str(scenario) + "_" + str(bus) + "_" +
                                          str(location) + "_" + str(time_stamp))

                            # coefficient for the y variable will be the price of the energy at that time stamp
                            objective_coefficient = np.asarray(
                                [parameters.Solar_energy_price * parameters.scale_factor_objective],
                                dtype=np.float64) * probability

                            # adding the y variable to the model
                            index_y = model.variables.add(obj=objective_coefficient, names=[y_variable], types=["C"],
                                                          lb=[0],
                                                          ub=[parameters.Solar_battery_charging_rate])

                            # annotation for the benders cut
                            if bender:
                                model.long_annotations.set_values(benders_annotation, object_type, list(index_y)[0],
                                                                  scenario)

                            # introducing the maximum energy transfer constraint EQUATION 10 in the paper
                            constraint_names = [f"maximum_transfer_{scenario}_{bus}_{location}_{time_stamp}"]

                            # constraint index for the energy transfer constraint
                            constraint_indices = [list(index_y)[0], list(index_x)[0]]

                            # maximum energy transfer constraint either from grid or solar
                            list_coefficient = [1 * parameters.scale_factor_constraints,
                                                1 * parameters.scale_factor_constraints]
                            constraint_direction = ['L']
                            rhs = [parameters.Charging_rate * parameters.scale_factor_constraints]
                            model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=constraint_indices,
                                                                                    val=list_coefficient)],
                                                         senses=constraint_direction,
                                                         rhs=rhs,
                                                         names=constraint_names)

                            # adding index and coefficient for the y variable for that charging opportunity/event
                            dict_solar_index[scenario][time_stamp][location].append(list(index_y)[0])
                            #################################################################################
                            list_index_energy.append(list(index_y)[0])
                            list_coefficient_energy.append(-1 * parameters.scale_factor_constraints)
                            ################################################################################

                    # constraint name for energy level EQUATIONS 4 & 12 from the paper
                    constraint_name_energy = [f"constraint_energy_{scenario}_{bus}_{charging_opportunity}"]

                    # initializing the energy level variable
                    string_name_energy = 'u' + "_" + str(scenario) + "_" + str(bus) + "_" + str(charging_opportunity)

                    # adding energy level variable except for last charging event
                    if charging_opportunity != last_charging_event:
                        index_energy = list(model.variables.add(names=[string_name_energy],
                                                                lb=[parameters.Min_battery_capacity],
                                                                ub=[parameters.Max_battery_capacity], types=["C"]))[0]

                        if charging_opportunity == 1:
                            index_scenario_bus[scenario][bus] = index_energy

                        # adding annotation if benders cut is applied
                        if bender:
                            model.long_annotations.set_values(benders_annotation, object_type, index_energy, scenario)

                    # for 1st charging event, introducing the last charging event energy level variable for periodicity
                    if charging_opportunity == 1:
                        last_event_string = "u" + "_" + str(scenario) + "_" + str(bus) + "_" + str(last_charging_event)
                        last_index_energy = list(model.variables.add(names=[last_event_string],
                                                                     lb=[parameters.Min_battery_capacity],
                                                                     ub=[parameters.Max_battery_capacity],
                                                                     types=["C"]))[0]

                        if last_charging_event == 1:
                            index_scenario_bus[scenario][bus] = last_index_energy

                        # adding annotation if benders cut is applied
                        if bender:
                            model.long_annotations.set_values(benders_annotation, object_type, last_index_energy,
                                                              scenario)

                        # adding index and coefficient for the last charging event energy level variable
                        if len(time_stamps_for_charging_opportunity) > 1:
                            list_index_energy.append(last_index_energy)
                            list_coefficient_energy.append(-1 * parameters.scale_factor_constraints)
                        else:
                            pass

                    # else allowing previous charging event energy level variable
                    else:
                        list_index_energy.append(previous_charging_event_stamp_index)
                        list_coefficient_energy.append(-1 * parameters.scale_factor_constraints)

                    # for max allowed energy transfer, extracting the index and
                    # coefficient from the list index and coefficient
                    constraint_indices_max = [i for i in list_index_energy]
                    list_coefficient_max = [-i for i in list_coefficient_energy]

                    # if there is only one charging event, then the first and last energy level variable will be same
                    if len(time_stamps_for_charging_opportunity) > 1:
                        list_coefficient_energy.append(1 * parameters.scale_factor_constraints)
                        if charging_opportunity == last_charging_event:
                            list_index_energy.append(last_index_energy)
                        else:
                            list_index_energy.append(index_energy)
                    else:
                        pass

                    # adding direction and rhs for the energy level constraint
                    constraint_direction = ["E"]
                    # print(scenario, bus, charging_opportunity)
                    rhs = [-dict_energy[scenario][bus][charging_opportunity] * parameters.scale_factor_constraints]
                    model.linear_constraints.add(
                        lin_expr=[cplex.SparsePair(ind=list_index_energy, val=list_coefficient_energy)],
                        senses=constraint_direction,
                        rhs=rhs,
                        names=constraint_name_energy)
                    ###########################################################################################
                    # max energy level constraint
                    # EQUATION 5 from the paper
                    constraint_name_max_energy = [f"maximum_energy_{scenario}_{bus}_{charging_opportunity}"]
                    constraint_direction = ["L"]
                    rhs = [parameters.Max_battery_capacity * parameters.scale_factor_constraints]
                    model.linear_constraints.add(
                        lin_expr=[cplex.SparsePair(ind=constraint_indices_max, val=list_coefficient_max)],
                        senses=constraint_direction,
                        rhs=rhs,
                        names=constraint_name_max_energy)

                # storing the current energy level variable index for the next charging event
                previous_charging_event_stamp_index = index_energy

            # constraint_name = [f"bus_equality_{scenario}_{bus}"]
            # constraint_direction = ["E"]
            # rhs = [0 * parameters.scale_factor_constraints]
            # list_c = [1 * parameters.scale_factor_constraints, -1 * parameters.scale_factor_constraints]
            # list_ind = [index_scenario_bus[scenario][bus], bus_battery_start[bus]]
            # model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=list_ind, val=list_c)],
            #                              senses=constraint_direction,
            #                              rhs=rhs,
            #                              names=constraint_name)
            constraint_name = [f"bus_g_equality_{scenario}_{bus}"]
            constraint_direction = ["G"]
            rhs = [parameters.Max_battery_capacity * parameters.scale_factor_constraints - dict_energy[scenario][bus][
                1] * parameters.scale_factor_constraints]
            list_c = [1 * parameters.scale_factor_constraints]
            list_ind = [index_scenario_bus[scenario][bus]]
            model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=list_ind, val=list_c)],
                                         senses=constraint_direction,
                                         rhs=rhs,
                                         names=constraint_name)

            constraint_name = [f"bus_l_equality_{scenario}_{bus}"]
            constraint_direction = ["L"]
            rhs = [parameters.Max_battery_capacity * parameters.scale_factor_constraints - dict_energy[scenario][bus][
                1] * parameters.scale_factor_constraints]
            list_c = [1 * parameters.scale_factor_constraints]
            list_ind = [index_scenario_bus[scenario][bus]]
            model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=list_ind, val=list_c)],
                                         senses=constraint_direction,
                                         rhs=rhs,
                                         names=constraint_name)

    return model, dict_grid_index, dict_solar_index


def add_grid_capacity_constraints(model,
                                  dict_grid: dict,
                                  dict_grid_index: dict,
                                  dict_grid_to_battery_index: dict):
    """
    adds grid capacity constraints at each time stamp where buses are available at the grid
    :param model: cplex model
    :param dict_grid: time_stamp wise buses available at grid
    :param dict_grid_index: corresponding index of the buses
    :param dict_grid_to_battery_index: index of grid to battery variables
    :return:
    model: cplex model with grid constraints
    """

    # iterating over the scenarios
    for scenario, time_stamps_wise_buses_at_locations in tqdm(dict_grid.items(),
                                                              desc="Adding scenarios wise grid capacity constraints"):

        # iterating over the time stamp where buses are available at the grid
        for time_stamp, location_wise_buses in time_stamps_wise_buses_at_locations.items():

            # for each location where buses are available at the grid
            for location, buses in location_wise_buses.items():
                # grid capacity variable
                grid_capacity_variable = "z" + "_" + str(location)

                # coefficient for the energy level variable will be 60
                list_coefficient = [60 * parameters.scale_factor_constraints for _ in range(len(buses))]

                # extracting the index of the grid capacity variable
                buses.append(dict_grid_index[grid_capacity_variable])
                # print(grid_capacity_variable)
                # print(dict_grid_index[grid_capacity_variable])

                # adding the grid capacity constraint
                list_coefficient.append(-1 * parameters.scale_factor_constraints)

                # print(dict_grid_to_battery_index[scenario][time_stamp][location])
                if dict_grid_to_battery_index is None:
                    pass
                else:
                    buses.append(dict_grid_to_battery_index[scenario][time_stamp][location][0])
                    list_coefficient.append(60 * parameters.scale_factor_constraints)

                # ref EQUATION 9 in the paper (case where x variables are present)
                constraint_names = [f"grid_{scenario}_{location}_{time_stamp}"]
                constraint_direction = ["L"]
                rhs = [0 * parameters.scale_factor_constraints]
                model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=buses, val=list_coefficient)],
                                             senses=constraint_direction,
                                             rhs=rhs,
                                             names=constraint_names)
    return model


def add_solar_battery_level_and_max_energy_level_constraints(model,
                                                             scenarios: int,
                                                             dict_solar_time_stamp: dict,
                                                             charging_locations: set,
                                                             end_time_stamp: int,
                                                             dict_solar_index: dict,
                                                             dict_location_index: dict,
                                                             dict_start_time_stamp: dict,
                                                             dict_time_loc_non_bus: dict,
                                                             benders_annotation,
                                                             object_type,
                                                             bender: bool,
                                                             network: str,
                                                             probability=1 / 3):
    """
    adds solar battery constraints and maximum battery level constraints for each charging location
    :param model: cplex model
    :param scenarios: number of scenarios
    :param dict_solar_time_stamp: dictionary of solar charging time stamp
    :param charging_locations: list of charging locations
    :param end_time_stamp: last time stamp for the model
    :param dict_solar_index: dictionary of index corresponding to bus available at the depot for charging
    :param dict_location_index: dictionary of location index
    :param dict_start_time_stamp: dict of start time of the model
    :param dict_time_loc_non_bus: dictionary of timestamps where buses are not present at the charging location
    :param benders_annotation: annotation for benders cut
    :param object_type: type of variable for benders cut
    :param bender: boolean value to add benders cut or not
    :param network: name of the network
    :param probability: probability of the scenario
    :return:
    model: updated CPLEX model
    dict_grid_to_battery_index: Indices of grid to battery variables
    """

    # new variable indices
    dict_grid_to_battery_index = {}
    # for each scenario
    for scenario in range(1, scenarios + 1):
        dict_grid_to_battery_index[scenario] = {}

    # storing the index of the energy level variable for each charging location for the 1st time stamp
    # new formulation for battery level constraints
    battery_level_start_end = {}
    for scenario in tqdm(range(1, scenarios + 1), desc="Adding scenarios wise solar-powered battery constraints "
                                                       "for charging locations"):

        for location in charging_locations:
            # to track the previous energy level variable
            previous_energy_stamp = str()
            index_previous = int()
            area_string = "a" + "_" + str(location)
            battery_capacity = "s" + "_" + str(location)

            # index corresponding to 1st stage variable
            index_area = dict_location_index[area_string]
            index_battery = dict_location_index[battery_capacity]

            # index corresponding to last time stamp
            last_time_stamp = "v" + "_" + str(scenario) + "_" + str(location) + "_" + str(end_time_stamp)
            index_energy_last = list(model.variables.add(names=[last_time_stamp], lb=[0], types=["C"]))[0]

            # adding annotation if benders cut is applied
            if bender:
                model.long_annotations.set_values(benders_annotation, object_type, index_energy_last, scenario)

            # to keep the battery level consistent across the scenarios
            if location not in battery_level_start_end:

                # energy level variable for location
                constant_energy = "d" + "_" + str(location)
                index_energy_l = list(
                    model.variables.add(names=[constant_energy], lb=[parameters.lower_bound_master_variables],
                                        ub=[parameters.upper_bound_master_variables],
                                        types=["C"]))[0]
                battery_level_start_end[location] = index_energy_l

                # adding annotation if benders cut is applied
                if bender:
                    model.long_annotations.set_values(benders_annotation, object_type, index_energy_l, 0)

            # if location in dict_depot[scenario]:
            #     start_time = start_t[scenario]
            # else:
            #     start_time = start_time_non_depot

            # for each time stamp starting from the 1st time stamp
            start_time = dict_start_time_stamp[scenario]
            # print(start_time, end_time_stamp)
            for time_stamp in range(start_time, end_time_stamp + 1):
                # index to be stored in the following list
                if time_stamp not in dict_grid_to_battery_index[scenario]:
                    dict_grid_to_battery_index[scenario][time_stamp] = {}
                if location not in dict_grid_to_battery_index[scenario][time_stamp]:
                    dict_grid_to_battery_index[scenario][time_stamp][location] = []
                list_coefficient = []
                list_index = []
                # energy level variable
                string_name = "v" + "_" + str(scenario) + "_" + str(location) + "_" + str(time_stamp)
                # if time_stamp is not the last time stamp, then add energy level variable
                if time_stamp != end_time_stamp:
                    index_energy = list(model.variables.add(names=[string_name], lb=[0], types=["C"]))[0]
                    # adding annotation if benders cut is applied
                    if bender:
                        model.long_annotations.set_values(benders_annotation, object_type, index_energy, scenario)
                        # adding index and coefficient for the energy level variable

                else:
                    index_energy = index_energy_last

                # add new variables for grid to battery
                # list_coefficient_grid_to_battery = []
                # list_index_grid_to_battery = []
                objective_coefficient = np.asarray([tou_pricing_time_stamp_wise(time_stamp,
                                                                                scenario, scenarios,
                                                                                network) * parameters.scale_factor_objective],
                                                   dtype=np.float64) * probability
                string_name_grid_to_battery = "h" + "_" + str(scenario) + "_" + str(location) + "_" + str(time_stamp)
                index_grid_to_battery = \
                    list(model.variables.add(obj=objective_coefficient, names=[string_name_grid_to_battery], lb=[0],
                                             types=["C"], ub=[cplex.infinity]))[0]

                dict_grid_to_battery_index[scenario][time_stamp][location].append(index_grid_to_battery)

                # add constraints of the form 60 h_{scenario, location, time_stamp} <= z_{location}
                # refer to EQUATION 9 in the paper (case where buses are not present at the charging location)
                if dict_time_loc_non_bus[scenario][time_stamp][location] == 1:
                    constraint_name_new = [f"only_grid_to_battery_{scenario}_{location}_{time_stamp}"]
                    constraint_direction_new = ["L"]
                    rhs_new = [0 * parameters.scale_factor_constraints]
                    list_c_new = [60 * parameters.scale_factor_constraints, -1 * parameters.scale_factor_constraints]
                    grid_capacity_variable = "z" + "_" + str(location)
                    list_ind_new = [index_grid_to_battery, dict_location_index[grid_capacity_variable]]
                    # add the constraint
                    model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=list_ind_new, val=list_c_new)],
                                                 senses=constraint_direction_new,
                                                 rhs=rhs_new,
                                                 names=constraint_name_new)

                if bender:
                    model.long_annotations.set_values(benders_annotation, object_type, index_grid_to_battery, scenario)

                # adding constraint at the last time stamp
                if time_stamp == end_time_stamp:
                    # add equality constraint for the last time stamp across the scenarios, first and last stamp
                    # energy are being updated in other loop
                    # refer EQUATION 13  in the paper
                    constraint_name = [f"battery_equality_{scenario}_{location}_{end_time_stamp}"]
                    constraint_direction = ["E"]
                    rhs = [0 * parameters.scale_factor_constraints]
                    list_c = [1 * parameters.scale_factor_constraints, -1 * parameters.scale_factor_constraints]
                    list_ind = [index_energy, battery_level_start_end[location]]
                    model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=list_ind, val=list_c)],
                                                 senses=constraint_direction,
                                                 rhs=rhs,
                                                 names=constraint_name)

                # adding index and coefficient of the energy level variable
                list_index.append(index_energy)
                list_coefficient.append(1 * parameters.scale_factor_constraints)

                # adding index and coefficient of corresponding bus available at the depot for charging
                if time_stamp in dict_solar_index[scenario]:
                    try:
                        if len(dict_solar_index[scenario][time_stamp][location]) > 0:
                            list_index = list_index + dict_solar_index[scenario][time_stamp][location]
                            list_coefficient = list_coefficient + [1 * parameters.scale_factor_constraints for _ in
                                                                   range(len(dict_solar_index[scenario][time_stamp][
                                                                                 location]))]
                    except KeyError:
                        pass

                # adding index and coefficient of previous energy level variable, in the 1st time_stamp, it will be the
                # last energy level variable that will be having the same index as the last energy level variable
                if previous_energy_stamp == '':
                    index_previous = index_energy_last

                # adding index and coefficient of the previous energy level variable
                list_index.append(index_previous)
                list_coefficient.append(-1 * parameters.scale_factor_constraints)

                # adding area variable index and coefficient
                list_index.append(index_area)
                coefficient = (-dict_solar_time_stamp[location][scenario][which_hour(time_stamp)]
                               * parameters.Efficiency_solar_panel * parameters.area_scale)
                list_coefficient.append(coefficient * parameters.scale_factor_constraints)

                # add the grid to battery index
                list_index.append(index_grid_to_battery)
                list_coefficient.append(-1 * parameters.scale_factor_constraints)

                # refer EQUATION 6 in the paper
                constraint_names = [f"battery_level_{scenario}_{location}_{time_stamp}"]

                # adding the direction and rhs for the constraint
                rhs = [0 * parameters.scale_factor_constraints]
                constraint_direction = ["E"]
                model.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=list_index, val=list_coefficient)],
                    senses=constraint_direction,
                    rhs=rhs,
                    names=constraint_names)
                ####################################################################################################
                # refer EQUATION 7 in the paper
                constraint_names = [f"solar_powered_{scenario}_{location}_{time_stamp}"]

                # index and coefficient will be stored in the following list
                list_coefficient = []
                list_index = []

                # battery capacity related variable index and coefficient
                list_coefficient.append(-1 * parameters.scale_factor_constraints)
                list_index.append(index_battery)

                # last energy level variable index and coefficient
                list_coefficient.append(1 * parameters.scale_factor_constraints)
                list_index.append(index_previous)

                # solar energy produced index and coefficient based on area and solar radiation
                # here 60 is not considered as I have already divided GTI by 60
                list_index.append(index_area)
                coefficient = (dict_solar_time_stamp[location][scenario][which_hour(time_stamp)]
                               * parameters.Efficiency_solar_panel * parameters.area_scale)
                list_coefficient.append(coefficient * parameters.scale_factor_constraints)

                # add the grid to battery index
                list_index.append(index_grid_to_battery)
                list_coefficient.append(1 * parameters.scale_factor_constraints)

                rhs = [0 * parameters.scale_factor_constraints]
                constraint_direction = ["L"]

                model.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=list_index, val=list_coefficient)],
                    senses=constraint_direction,
                    rhs=rhs,
                    names=constraint_names)
                ####################################################################################################
                ##### dod constraint ##########
                # refer EQUATION 8 in the paper
                constraint_names = [f"dod_{scenario}_{location}_{time_stamp}"]
                # index and coefficient will be stored in the following list
                list_coefficient = []
                list_index = []

                # battery capacity related variable index and coefficient
                list_coefficient.append(-(1 - parameters.depth_of_discharge) * parameters.scale_factor_constraints)
                list_index.append(index_battery)
                # adding index and coefficient of the energy level variable
                list_index.append(index_energy)
                list_coefficient.append(1 * parameters.scale_factor_constraints)
                rhs = [0 * parameters.scale_factor_constraints]
                constraint_direction = ["G"]
                model.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=list_index, val=list_coefficient)],
                    senses=constraint_direction,
                    rhs=rhs,
                    names=constraint_names)
                ####################################################################################################
                previous_energy_stamp = string_name
                index_previous = index_energy

    return model, dict_grid_to_battery_index


def build_and_solve_scenario_based_csp(dict_charging_opportunity_time_stamp,
                                       dict_solar_time_stamp,
                                       dict_energy_required,
                                       charging_locations,
                                       end_time_stamp,
                                       dict_time_stamp_grid,
                                       start_time_stamp,
                                       dict_loc_time_non_bus,
                                       bus_list_overall,
                                       variable_type,
                                       benders_strategy,
                                       parallel_mode,
                                       network_name,
                                       apply_benders_cut,
                                       scenarios,
                                       probability,
                                       use_temperature,
                                       use_renewables,
                                       dict_network_name,
                                       run_id,
                                       model_time_limit=172800):
    """
    This function creates the optimisation model for the charging scheduling problem
    :param dict_charging_opportunity_time_stamp: dictionary of bus number and charging event wise time stamp
    :param dict_solar_time_stamp: dictionary of solar charging time stamp
    :param dict_energy_required: dictionary of energy required for each charging event
    :param charging_locations: list of charging locations
    :param end_time_stamp: last time stamp for the model
    :param dict_time_stamp_grid: dictionary of timestamp wise buses available at grid
    :param start_time_stamp: scenario-wise dict of start time of the model
    :param dict_loc_time_non_bus: dictionary of timestamps where buses are not present at the charging location
    :param bus_list_overall: list of total buses available
    :param variable_type: type of variable continuous or Integer
    :param benders_strategy: benders strategy to be applied
    :param parallel_mode: parallel mode type
    :param network_name: name of the network
    :param apply_benders_cut: whether to add benders cut or not
    :param scenarios: number of scenarios to be considered for solar energy production
    :param probability: probability of the scenario
    :param use_temperature: temperature variations considered or not
    :param use_renewables: renewable energy integration considered or not
    :param dict_network_name: dictionary of network names
    :param run_id: run id
    :param model_time_limit: time limit for the model
    :return:
    model: cplex model
    solution_data: solution information
    """

    # initializing the model and its objective sense
    model = cplex.Cplex()
    model.objective.set_sense(model.objective.sense.minimize)
    # adding annotation for benders cut
    if apply_benders_cut:
        benders_annotation = model.long_annotations.add(name="cpxBendersPartition", defval=0)
        object_type = model.long_annotations.object_type.variable
    else:
        benders_annotation = None
        object_type = None

    # time the model
    start_watch = time.time()
    print("####################")
    print(f"Network {network_name}")
    print("####################")

    # initializing 1st stage variable
    start_time1 = time.time()
    model, dict_location_index = add_first_stage_variables(model,
                                                           charging_locations,
                                                           variable_type,
                                                           benders_annotation,
                                                           object_type,
                                                           apply_benders_cut,
                                                           renewable=use_renewables)
    end_time1 = time.time()
    time_taken1 = end_time1 - start_time1

    # add decision variables for each scenario
    start_time2 = time.time()
    model, dict_grid_index, dict_solar_index = add_decision_variables_and_bus_energy_level_constraints(model,
                                                                                                       scenarios,
                                                                                                       dict_charging_opportunity_time_stamp,
                                                                                                       dict_energy_required,
                                                                                                       dict_time_stamp_grid,
                                                                                                       apply_benders_cut,
                                                                                                       benders_annotation,
                                                                                                       object_type,
                                                                                                       network_name,
                                                                                                       bus_list_overall,
                                                                                                       probability,
                                                                                                       renewable=use_renewables)
    end_time2 = time.time()
    time_taken2 = end_time2 - start_time2

    # print(dict_grid_index)

    if use_renewables:
        # solar related constraints
        start_time7 = time.time()
        model, dict_grid_to_battery_index = add_solar_battery_level_and_max_energy_level_constraints(model,
                                                                                                     scenarios,
                                                                                                     dict_solar_time_stamp,
                                                                                                     charging_locations,
                                                                                                     end_time_stamp,
                                                                                                     dict_solar_index,
                                                                                                     dict_location_index,
                                                                                                     start_time_stamp,
                                                                                                     dict_loc_time_non_bus,
                                                                                                     benders_annotation,
                                                                                                     object_type,
                                                                                                     apply_benders_cut,
                                                                                                     network_name,
                                                                                                     probability)
        end_time7 = time.time()
        time_taken7 = end_time7 - start_time7
    else:
        dict_grid_to_battery_index = None
        time_taken7 = 0

    # add grid capacity constraint
    start_time6 = time.time()
    model = add_grid_capacity_constraints(model,
                                          dict_grid_index,
                                          dict_location_index,
                                          dict_grid_to_battery_index)
    end_time6 = time.time()
    time_taken6 = end_time6 - start_time6

    end_watch = time.time()
    time_taken = end_watch - start_watch

    # get key from the dictionary having network_name
    network_short_name = dict_network_name.get(network_name)

    model.set_problem_name(f"csp_{network_short_name}_{scenarios}_scenarios_"
                           f"benders_{apply_benders_cut}_temperature_{use_temperature}_renewables_{use_renewables}")

    # scaling starts
    # Step 1: Get the original ranges
    rows = model.linear_constraints.get_rows()
    rhs_values = model.linear_constraints.get_rhs()
    # Step 2: Scale the coefficients and RHS by the max value in each row
    scaled_rows, scaled_rhs = scale_model(rows, rhs_values, scaling_choice="max", new_min=1, new_max=1000)
    model = update_model(model, scaled_rows, scaled_rhs)
    # scaling ends

    # set time limit for the model
    model.parameters.timelimit.set(model_time_limit)
    # model.parameters.emphasis.numerical.set(1)
    model.set_problem_type(cplex.Cplex.problem_type.LP)
    print("Problem type is ", model.get_problem_type())

    # strategy for benders cut
    if apply_benders_cut:
        # model.long_annotations("cpxBendersPartition").set(1)
        # set benders parameter to 3
        # model.read_annotations(f"./{network}/csp_{network}_{scenarios}.ann")
        model.parameters.benders.strategy.set(int(benders_strategy))
        # # set the tolerance for the feasibility cut
        model.parameters.benders.tolerances.feasibilitycut.set(1e-06)
        # set the tolerance for the optimality cut
        model.parameters.benders.tolerances.optimalitycut.set(1e-06)
        # print the tolerance for the feasibility cut
        print("Feasibility cut tolerance is ", model.parameters.benders.tolerances.feasibilitycut.get())
        # print the tolerance for the optimality cut
        print("Optimality cut tolerance is ", model.parameters.benders.tolerances.optimalitycut.get())
        # write the .ann file
        model.write_annotations(
            f"./{network_name}/{scenarios}_scenario/csp_{network_name}_{scenarios}_manual.ann")
        # model.write_benders_annotation(f"./{network}/csp_{network}_{scenarios}_auto.ann")

    print("type of variable is ", variable_type)
    print("benders is applied ", apply_benders_cut)
    print("benders strategy is ", benders_strategy)

    # switch the parallel mode on
    model.parameters.parallel.set(int(parallel_mode))
    # model.parameters.threads.set(int(core))

    # set the lp method to primal simplex
    model.parameters.lpmethod.set(2)  # 1 for primal and 2 for dual
    # for ind in range(1, len(master_indices_list)):
    #     model.variables.set_lower_bounds(master_indices_list[ind], master_values_list[ind])
    #     model.variables.set_upper_bounds(master_indices_list[ind], master_values_list[ind])
    model.parameters.read.scale.set(0)  # default scaling of CPLEX

    if use_temperature:
        # write model in lp format
        model.write(f"./{network_name}/{scenarios}_scenario/csp_{network_short_name}_"
                    f"{scenarios}_scenarios_benders_{apply_benders_cut}_temperature_{use_temperature}_"
                    f"renewables_{use_renewables}.lp")

    else:
        # write model in lp format
        model.write(f"./{network_name}/without_temperature/1_scenario/csp_{network_short_name}_"
                    f"{scenarios}_scenarios_benders_{apply_benders_cut}_temperature_{use_temperature}_"
                    f"renewables_{use_renewables}.lp")

    # model.parameters.threads.set(int(core))

    # Open a file to save the output
    with open(f"output_{network_name}_{scenarios}_scenarios_benders_{apply_benders_cut}_renewables_{use_renewables}.txt", "w") as output_file:
        # Set the log stream and results stream to the output file
        model.set_log_stream(output_file)
        model.set_results_stream(output_file)

        # Optional: You can also set error and warning streams if needed
        model.set_error_stream(output_file)
        model.set_warning_stream(output_file)

        # time the model
        s_t = time.time()
        # solve the model
        # turn off the presolve
        # model.parameters.preprocessing.presolve.set(0)
        model.solve()
        e_t = time.time()
        time_ = e_t - s_t
        print(f"Time taken to solve the model is {time_ / 60} minutes")

        # Reset streams before exiting the block (IMPORTANT)
        model.set_log_stream(None)
        model.set_results_stream(None)
        model.set_error_stream(None)
        model.set_warning_stream(None)

    if use_temperature:
        # write model in lp format
        # model.write(f"./{network_name}/{scenarios}_scenario/csp_{network_short_name}_"
        #             f"{scenarios}_scenarios_benders_{apply_benders_cut}_temperature_{use_temperature}_"
        #             f"renewables_{use_renewables}.lp")
        # write the solution in sol format
        model.solution.write(f"./{network_name}/{scenarios}_scenario/csp_{network_short_name}_"
                             f"{scenarios}_benders_{apply_benders_cut}_temperature_{use_temperature}_"
                             f"renewables_{use_renewables}.sol")
    else:
        # write model in lp format
        # model.write(f"./{network_name}/without_temperature/1_scenario/csp_{network_short_name}_"
        #             f"{scenarios}_scenarios_benders_{apply_benders_cut}_temperature_{use_temperature}_"
        #             f"renewables_{use_renewables}.lp")
        # write the solution in sol format
        model.solution.write(
            f"./{network_name}/without_temperature/1_scenario/csp_{network_short_name}_{scenarios}_"
            f"scenarios_benders_{apply_benders_cut}_temperature_{use_temperature}_renewables_{use_renewables}.sol")
    # # .mps file
    # model.write(f"./{network}/scenario_{scenarios}/csp_{dict_network_short_name[network]}_{scenarios}_scenarios_"
    #             f"{len(dict_charging_opportunity_time_stamp)}_buses_.mps")
    # print the time taken to create the mode
    # save the time taken to create the model in .txt file
    print(f"Time taken to create model is {time_taken} seconds")
    print(f"Time taken to create first stage model is {time_taken1} seconds")
    print(f"Time taken to add decision variables is {time_taken2} seconds")
    print(f"Time taken to add grid capacity constraints is {time_taken6} seconds")
    print(f"Time taken to add solar-powered battery and maximum capacity constraints is {time_taken7} seconds")
    # print(f"Time taken to add max solar-powered battery capacity constraints is {time_taken8} seconds")
    # get the values of the variables
    variable_names = model.variables.get_names()
    print(f"Number of variables in millions are {round(len(variable_names) / 1000000, 3)}")
    constraint_name = model.linear_constraints.get_names()
    print(f"Number of constraints in millions are {round(len(constraint_name) / 1000000, 3)}")
    variable_values = model.solution.get_values()
    objective_value = model.solution.get_objective_value()
    print(f"Objective value in $ is {objective_value * parameters.Euros_to_dollars_exchange_rate}")
    # if use_temperature:
    #     log_file = (f"./{network_name}/{scenarios}_scenario/time_taken_{network_short_name}"
    #                 f"_{scenarios}_scenarios_benders_{apply_benders_cut}_temperature_"
    #                 f"{use_temperature}_renewables_{use_renewables}.txt")
    # else:
    #     log_file = (f"./{network_name}/without_temperature/1_scenario/time_taken_"
    #                 f"{network_short_name}_{scenarios}_scenarios_benders_"
    #                 f"{apply_benders_cut}_temperature_{use_temperature}_renewables_{use_renewables}.txt")
    # with open(log_file, 'w') as file:
    #     file.write(f"Network {network_name}\n")
    #     file.write(f'Time stamp at which the model is created is {time.asctime()}\n')
    #     file.write(f"Time taken to create model is {time_taken} seconds\n")
    #     file.write(f"Time taken to create first stage model is {time_taken1} seconds\n")
    #     file.write(f"Time taken to add decision variables is {time_taken2} seconds\n")
    #     file.write(f"Time taken to add grid capacity constraints is {time_taken6} seconds\n")
    #     file.write(f"Time taken to add solar-powered battery and maximum capacity constraints is {time_taken7} seconds\n")
    #     file.write(f'Number of variables in millions are {round(len(variable_names)/1000000, 3)}\n')
    #     file.write(f'Number of constraints in millions are {round(len(constraint_name)/1000000, 3)}\n')
    #     file.write(f"Objective value in $ is {objective_value * parameters.Euros_to_dollars_exchange_rate}\n")
    #     file.write(f"Time taken to solve the model is {time_/60} minutes\n")

    # open log file in the main folder
    log_file_main = pd.read_csv(f"./log_file.csv")
    log_file_main.loc[len(log_file_main)] = [run_id,
                                             time.asctime(),
                                             network_name,
                                             scenarios,
                                             objective_value * parameters.Euros_to_dollars_exchange_rate,
                                             time_ / 60,
                                             time_taken,
                                             round(len(variable_names) / 1000000, 3),
                                             round(len(constraint_name) / 1000000, 3),
                                             model.solution.get_status_string(),
                                             apply_benders_cut,
                                             use_temperature,
                                             use_renewables,
                                             parameters.Unit_panel_cost,
                                             parameters.Unit_battery_price,
                                             parameters.Unit_capacity_cost
                                             ]
    log_file_main.to_csv(f"./log_file.csv", index=False)
    # storing the solutions in a dictionary
    constraint_slack_value = model.solution.get_linear_slacks()
    dict_variable = {}
    for i in range(len(variable_names)):
        dict_variable[variable_names[i]] = variable_values[i]

    dict_constraint_slack_value = {}
    for i in range(len(constraint_name)):
        dict_constraint_slack_value[constraint_name[i]] = constraint_slack_value[i]

    solution_data = {"variable_name_values": dict_variable,
                     "objective_value": objective_value,
                     "constraint_slack_value": dict_constraint_slack_value}

    return model, solution_data
