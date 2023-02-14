import numpy as np
import scipy as sc

class Tableau():

    """
    Constructs, manipulates, and outputs information about a simplex tableau.

    Constructs an initial tableau from data Ax <= b and profit function c^Tx.
    Computes pivot column, theta_column, pivot_row, and performs row operations
    Outputs basic and non-basic variables, profit, values, and the whole tableau
    """

    debug_theta = False

    valid_theta_signs = np.array([[False, False, False],
                                  [True, True, False],
                                  [False, False, True]])

    def __init__(self, global_problem, dimension, profit_vector):
        self.dimension = dimension
        self.global_problem = global_problem
        self.constraint_matrix = global_problem.constraint_matrix
        self.constraint_vector = global_problem.constraint_vector
        self.profit_vector = profit_vector
        self.initialise_problem_from_input_data()
        self.pivot_column_index = None

    def initialise_problem_from_input_data(self):
        self.set_dimensions()
        self.set_spatial_and_non_spatial_variables()
        self.initialise_basic_and_non_basic_variables()
        self.set_tableau_data()

    def set_dimensions(self):
        self.space_dimensions = self.constraint_matrix.shape[1]
        self.slack_dimensions = self.constraint_matrix.shape[0]
        self.total_dimensions = self.space_dimensions + self.slack_dimensions

    def set_spatial_and_non_spatial_variables(self):
        self.spatial_variables = np.array(range(self.space_dimensions))
        self.slack_variables = np.array(range(self.space_dimensions, self.total_dimensions))

    def initialise_basic_and_non_basic_variables(self):
        self.non_basic_variables = np.array(range(self.space_dimensions))
        self.basic_variables = np.array(range(self.space_dimensions, self.total_dimensions))

    def set_tableau_data(self):
        self.values = np.copy(self.constraint_vector)
        self.profit = 0
        self.tableau = np.concatenate((self.constraint_matrix,
                                       np.identity(self.slack_dimensions)),
                                      axis=1)

    def set_tableau_components(self):
        self.set_column_filtered_arrays()
        self.A_basic_LU, self.A_permute = sc.linalg.lu_factor(self.A_basic)
        self.set_values()
        self.set_pivot_column()
        self.set_profit_row()
        self.profit = self.get_profit()
    
    def set_column_filtered_arrays(self):
        self.A_basic = self.tableau[:, self.basic_variables]
        self.A_non_basic = self.tableau[:, self.non_basic_variables]
        self.c_basic = self.profit_vector[self.basic_variables]
        self.c_non_basic = self.profit_vector[self.non_basic_variables]

    def set_values(self):
        self.values = sc.linalg.lu_solve((self.A_basic_LU, self.A_permute),
                                         self.constraint_vector)
    
    def set_pivot_column(self):
        pivot_column = self.tableau[:, self.pivot_column_index]
        self.pivot_column = sc.linalg.lu_solve((self.A_basic_LU, self.A_permute),
                                               pivot_column)

    def set_profit_row(self):
        intermediate_vector = sc.linalg.lu_solve((self.A_basic_LU, self.A_permute),
                                                 self.c_basic, trans = 1)
        self.profit_row = self.c_non_basic - np.dot(np.transpose(self.A_non_basic),
                                                    intermediate_vector)

    def get_profit(self):
        profit = np.dot(self.c_basic, self.values)
        return profit

    def get_potential_profit(self):
        theta_column = self.get_theta_column()
        self.pivot_row_index = np.argmin(theta_column)
        potential_profit = self.process_theta_column(theta_column)
        return potential_profit

    def get_theta_column(self):
        self.set_pivot_column()
        valid_theta_array = self.get_valid_theta_array()
        pivot_column = np.where(valid_theta_array, self.pivot_column, 1)
        theta_column = np.where(valid_theta_array, self.values/pivot_column, np.inf)
        self.debug_theta_computation(theta_column, pivot_column, valid_theta_array)
        return theta_column

    def get_valid_theta_array(self):
        pivot_column_sign = np.sign(np.around(self.pivot_column, 4)).astype('int')
        value_column_sign = np.sign(np.around(self.values, 4)).astype('int')
        valid_theta_array = self.valid_theta_signs[pivot_column_sign, value_column_sign]
        return valid_theta_array

    def debug_theta_computation(self, theta_column, pivot_column_valid, valid_theta_array):
        if self.debug_theta:
            theta_computation_array = np.vstack((self.pivot_column,
                                                 pivot_column_valid,
                                                 self.values,
                                                 theta_column,
                                                 valid_theta_array))
            print(("Debugging theta computation. Columns are pivot column,\n"
                   "pivot column valid, values, theta, and whether theta is valid"))
            print(np.transpose(theta_computation_array))

    def process_theta_column(self, theta_column):
        if theta_column[self.pivot_row_index] == np.inf:
            potential_profit = -np.inf
        else:
            potential_profit = self.compute_potential_profit()
        return potential_profit

    def compute_potential_profit(self):
        pivot_value = self.pivot_column[self.pivot_row_index]
        profit_pivot_column = self.profit_row[self.pivot_column_index]
        value_pivot_row = self.values[self.pivot_row_index]
        profit_row_multiplier = profit_pivot_column/pivot_value
        potential_profit = self.profit - value_pivot_row*profit_row_multiplier
        return potential_profit

    def pivot(self):
        self.update_basic_and_non_basic_variables()
        self.set_tableau_components()
        self.set_pivot_column_index()

    def update_basic_and_non_basic_variables(self):
        exiting_variable = self.basic_variables[self.pivot_row_index]
        entering_variable = self.non_basic_variables[self.pivot_column_index]
        self.basic_variables[self.pivot_row_index] = entering_variable
        self.non_basic_variables[self.pivot_column_index] = exiting_variable

    def set_pivot_column_index(self):
        self.pivot_column_index = np.argmin(self.profit_row)
        if self.profit_row[self.pivot_column_index] == 0:
            print("Optimal!")

    def get_line_of_movement(self):
        line_reference_vector = self.get_line_reference_vector()
        line_direction_vector = self.get_line_direction_vector()

    def get_line_reference_vector(self):
        reference_vector = np.array([self.get_spatial_variable_value(dimension)
                                     for dimension in range(self.space_dimensions)])
        return reference_vector

    def get_spatial_variable_value(self, dimension):
        if dimension in self.basic_variables:
            index = self.basic_variables.index(dimension)
            value = self.basic_variables[index]
        else:
            value = 0
        print("Value: ", value)
        return value

    def get_line_direction_vector(self):
        constraint_indices = self.get_constraint_indices()
        print(constraint_indices)
        print(self.global_problem.space_constraints)

    def get_constraint_indices(self):
        constraint_indices = np.copy(self.non_basic_variables)
        removing_indices = constraint_indices == self.pivot_column_index
        constraint_indices = np.delete(constraint_indices, removing_indices)
        return constraint_indices

    def output_all(self):
        self.output_basic_and_non_basic_variables()
        self.output_matrices()
        self.output_values()
        self.output_profit_information()
        self.output_vertex_position()

    def output_basic_and_non_basic_variables(self):
        basic_variables_string = [str(round(value, 2)) for value in self.basic_variables]
        non_basic_variables_string = [str(round(value, 2)) for value in self.non_basic_variables]
        print((f"Outputting basic and non basic variables for dimension {self.dimension}\n"
               f"Basic variables: {', '.join(basic_variables_string)}\n"
               f"Non-basic variables: {', '.join(non_basic_variables_string)}\n"
               f"Pivot column index: {self.pivot_column_index}"))

    def output_values(self):
        print(f"Outputting values for dimension {self.dimension}")
        for basic_variable, value in zip(self.basic_variables, self.values):
            print(f"{basic_variable}: {round(value, 2)}")
        print("")

    def output_matrices(self):
        print(f"Outputting basic and non-basic matrices for dimension {self.dimension}")
        print(self.A_basic)
        print(self.A_non_basic)

    def output_vertex_position(self):
        print(f"Outputting vertex position for dimension {self.dimension}")
        self.set_basic_variable_spatial_dict()
        for spatial_variable in self.spatial_variables:
            spatial_variable_value = self.get_spatial_variable_value(spatial_variable)
            print(f"{spatial_variable}: {spatial_variable_value}")
        print("")

    def set_basic_variable_spatial_dict(self):
        basic_variable_spatial_dict = [(variable_name, self.values[index])
                                       for index, variable_name in enumerate(self.basic_variables)
                                       if variable_name in self.spatial_variables]
        self.basic_variable_spatial_dict = dict(basic_variable_spatial_dict)

    def get_spatial_variable_value(self, spatial_variable):
        if spatial_variable in self.basic_variables:
            value = self.basic_variables[self.basic_variables == spatial_variable][0]
        else:
            value = 0
        return value

    def output_profit_information(self):
        print(f"Outputting profit information for dimension {self.dimension}")
        print(f"Profit: {self.profit}")
        for non_basic_variable, profit_coefficient in zip(self.non_basic_variables, self.profit_row):
            print(f"{non_basic_variable}: {profit_coefficient}")
        print("")
