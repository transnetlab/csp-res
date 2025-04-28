"""
Used to find a suitable scale for the constraint coefficients and RHS values in a CPLEX model
"""

import cplex


# Function to load the model
def load_model(filepath):
    """
    :param filepath: path to the LP file
    :return:
    model: CPLEX model
    """
    model = cplex.Cplex()
    model.read(filepath)
    return model


# Function to get highest and lowest constraint coefficients
def get_constraint_coeff_ranges(rows):
    """
    :param rows: Rows of the constraint matrix
    :return:
    Information containing the highest and lowest positive and negative coefficients
    """
    positive_constraint_coeffs = []
    negative_constraint_coeffs = []

    for row in rows:
        for coeff in row.val:
            if coeff > 0:
                positive_constraint_coeffs.append(coeff)
            elif coeff < 0:
                negative_constraint_coeffs.append(coeff)

    return {
        "highest_positive": max(positive_constraint_coeffs, default=None),
        "lowest_positive": min(positive_constraint_coeffs, default=None),
        "highest_negative": max(negative_constraint_coeffs, default=None),
        "lowest_negative": min(negative_constraint_coeffs, default=None)
    }


# Function to get highest and lowest RHS values
def get_rhs_ranges(rhs_values):
    """
    :param rhs_values: RHS values of the constraints
    :return:
    Information containing the highest and lowest positive and negative RHS values
    """
    positive_rhs_values = [rhs for rhs in rhs_values if rhs > 0]
    negative_rhs_values = [rhs for rhs in rhs_values if rhs < 0]

    return {
        "highest_positive": max(positive_rhs_values, default=None),
        "lowest_positive": min(positive_rhs_values, default=None),
        "highest_negative": max(negative_rhs_values, default=None),
        "lowest_negative": min(negative_rhs_values, default=None)
    }


# Function to scale all coefficients and RHS in a row by the same scaling factor
def scale_row_and_rhs(row_coeffs, rhs_value, scale_factor):
    """
    :param row_coeffs: Coefficients of the constraint row
    :param rhs_value: RHS value of the constraint
    :param scale_factor: Scaling factor
    :return:
    scaled_coeffs: Scaled coefficients
    scaled_rhs: Scaled RHS value
    """
    scaled_coeffs = [coeff * scale_factor for coeff in row_coeffs]
    scaled_rhs = rhs_value * scale_factor
    return scaled_coeffs, scaled_rhs


# Function to scale the model based on row scaling factors
def scale_model(rows, rhs_values, scaling_choice="max", new_min=1, new_max=1000):
    """
    :paam rows: Rows of the constraint matrix
    :param rhs_values:  RHS values of the constraints
    :param scaling_choice: Choice of scaling factor (max or min)
    :param new_min: Minimum value for the scaled coefficients
    :param new_max: Maximum value for the scaled coefficients
    :return:
    scaled_rows: Scaled rows of the constraint matrix
    scaled_rhs: Scaled RHS values
    """
    scaled_rows = []
    scaled_rhs = []

    for row_idx, row in enumerate(rows):
        coeffs = row.val

        # Select the scaling factor (based on max or min coefficient)
        if scaling_choice == "max" and max(coeffs) > 0:
            scale_factor = new_max / max(coeffs)
        elif scaling_choice == "min":
            scale_factor = new_min / min(coeffs)
        else:
            scale_factor = 1

        # Scale the entire row and corresponding RHS by the scale factor
        scaled_coeffs, scaled_rhs_value = scale_row_and_rhs(coeffs, rhs_values[row_idx], scale_factor)

        # Append scaled values
        scaled_row = cplex.SparsePair(ind=row.ind, val=scaled_coeffs)
        scaled_rows.append(scaled_row)
        scaled_rhs.append(scaled_rhs_value)

    return scaled_rows, scaled_rhs


# Function to print the results
def print_ranges(ranges, label):
    """
    :param ranges: Dictionary containing the ranges
    :param label: Different labels (e.g., Constraint Coefficients, RHS Values)
    :return:
    """
    print(f"{label}:")
    print(f"  Highest Positive: {ranges['highest_positive']}")
    print(f"  Lowest Positive: {ranges['lowest_positive']}")
    print(f"  Highest Negative: {ranges['highest_negative']}")
    print(f"  Lowest Negative: {ranges['lowest_negative']}\n")


# # Sample implemetation
# model_new = load_model(
#     "./Durham_2.1k/3_scenario/csp_durham_3_scenarios_benders_False_temperature_True_renewables_True.lp")
#
# # Step 1: Get the original ranges
# rows = model_new.linear_constraints.get_rows()
# rhs_values = model_new.linear_constraints.get_rhs()
#
# constraint_ranges = get_constraint_coeff_ranges(rows)
# rhs_ranges = get_rhs_ranges(rhs_values)
#
# # Print original ranges
# print("Original Ranges:")
# print_ranges(constraint_ranges, "Constraint Coefficients")
# print_ranges(rhs_ranges, "RHS Values")
#
# # Step 2: Scale the coefficients and RHS by the max value in each row
# scaled_rows, scaled_rhs = scale_model(rows, rhs_values, scaling_choice="max", new_min=1, new_max=1)
#
# # Step 3: Get the new ranges after scaling
# scaled_constraint_ranges = get_constraint_coeff_ranges(scaled_rows)
# scaled_rhs_ranges = get_rhs_ranges(scaled_rhs)
#
# # Print scaled ranges
# print("Scaled Ranges:")
# print_ranges(scaled_constraint_ranges, "Scaled Constraint Coefficients")
# print_ranges(scaled_rhs_ranges, "Scaled RHS Values")


def update_model(model, scaled_rows, scaled_rhs):
    """
    :param model: Original CPLEX model
    :param scaled_rows: Scaled rows of the constraint matrix
    :param scaled_rhs: Scaled RHS values
    :return:
    model: Updated CPLEX model
    """
    for row_idx, scaled_row in enumerate(scaled_rows):
        for var_idx, coeff in zip(scaled_row.ind, scaled_row.val):
            model.linear_constraints.set_coefficients(row_idx, var_idx, coeff)

    for row_idx, scaled_rhs_value in enumerate(scaled_rhs):
        model.linear_constraints.set_rhs(row_idx, scaled_rhs_value)

    return model

# updated_model = update_model(model_new, scaled_rows, scaled_rhs)
