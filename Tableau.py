import numpy as np
import scipy.linalg as sc_la
import math

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
        # Maybe remove these later if they turn out to be unnecessary
        self.constraint_matrix = global_problem.constraint_matrix
        self.constraint_vector = global_problem.constraint_vector
        self.space_constraints = global_problem.space_constraints
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
        self.spatial_variables = np.arange(self.space_dimensions)
        self.slack_variables = np.arange(self.space_dimensions, self.total_dimensions)

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
        self.A_basic_LU, self.A_permute = sc_la.lu_factor(self.A_basic)
        self.set_values()
        self.set_pivot_column()
        self.set_profit_row()
        self.profit = self.get_profit()
    
    def set_column_filtered_arrays(self):
        self.A_basic = self.tableau[:, self.basic_variables]
        self.A_non_basic = self.tableau[:, self.non_basic_variables]
        self.c_basic = self.global_problem.profit_vector[self.basic_variables]
        self.c_non_basic = self.global_problem.profit_vector[self.non_basic_variables]

    def set_values(self):
        self.values = sc_la.lu_solve((self.A_basic_LU, self.A_permute),
                                         self.constraint_vector)
    
    def set_pivot_column(self):
        pivot_column = self.A_non_basic[:, self.pivot_column_index]
        self.pivot_column = sc_la.lu_solve((self.A_basic_LU, self.A_permute),
                                               pivot_column)

    def set_profit_row(self):
        intermediate_vector = sc_la.lu_solve((self.A_basic_LU, self.A_permute),
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
        self.pivot_value = self.pivot_column[self.pivot_row_index]
        potential_values = self.get_potential_values()
        potential_profit = math.sqrt(sum(np.array(potential_values)**2))
        return potential_profit

    def get_potential_values(self):
        potential_values = [self.get_potential_value(spatial_variable)
                            for spatial_variable in self.spatial_variables]
        return potential_values

    def get_potential_value(self, spatial_variable):
        if spatial_variable == self.non_basic_variables[self.pivot_column_index]:
            value = self.values[self.pivot_row_index] / self.pivot_column[self.pivot_row_index]
        elif spatial_variable in self.basic_variables:
            value = self.get_potential_spatial_basic_value(spatial_variable)
        else:
            value = 0
        return value

    def get_potential_spatial_basic_value(self, spatial_variable):
        basic_variable_index = np.where(self.basic_variables == spatial_variable)[0][0]
        multiplier = self.pivot_column[basic_variable_index] / self.pivot_column[self.pivot_row_index]
        value = self.values[basic_variable_index] - multiplier * self.values[self.pivot_row_index]
        return value

    def pivot(self):
        self.update_basic_and_non_basic_variables()
        self.set_tableau_components()

    def update_basic_and_non_basic_variables(self):
        exiting_variable = self.basic_variables[self.pivot_row_index]
        entering_variable = self.non_basic_variables[self.pivot_column_index]
        self.basic_variables[self.pivot_row_index] = entering_variable
        self.non_basic_variables[self.pivot_column_index] = exiting_variable

    def set_pivot_column_index(self):
        self.pivot_column_index = np.argmax(self.profit_row)
        self.set_pivot_column_index_to_dimension()
        self.check_if_problem_solved()

    def set_pivot_column_index_to_dimension(self):
        if self.dimension in self.non_basic_variables:
            dimension_index = np.where(self.non_basic_variables == self.dimension)[0][0]
            if self.profit_row[dimension_index] > -0.0001:
                self.pivot_column_index = dimension_index

    def check_if_problem_solved(self):
        if self.profit_row[self.pivot_column_index] <= 0.0001:
            self.global_problem.solved_status = "Optimal"

    def compute_partial_position(self):
        self.set_line_of_movement()
        self.find_hypersphere_intersection()

    def set_line_of_movement(self):
        self.line_reference_vector = self.get_line_reference_vector()
        self.set_line_direction_vector()
        
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
        return value

    def set_line_direction_vector(self):
        constraint_indices = self.get_constraint_indices()
        constraint_matrix = self.space_constraints[constraint_indices, :]
        null_space = sc_la.null_space(constraint_matrix)
        self.check_null_space(null_space)
        self.line_direction_vector = null_space[:, 0]

    def get_constraint_indices(self):
        constraint_indices = np.copy(self.non_basic_variables)
        constraint_indices = np.delete(constraint_indices, self.pivot_column_index)
        return constraint_indices

    def check_null_space(self, null_space):
        dimension_of_null_space = null_space.shape[1]
        if dimension_of_null_space != 1:
            raise Exception((f"Null space for dimension {self.dimension} is not 1 ({dimension_of_null_space})\n"
                             "Check that constraints are linearly independent"))

    def find_hypersphere_intersection(self):
        reference_abs, direction_abs, cross_term = self.get_vector_quantities()
        position_parameters = self.get_position_parameters(reference_abs, direction_abs, cross_term)
        position_plus, position_minus = self.get_positions(position_parameters)
        self.set_partial_position(position_plus, position_minus)

    def get_vector_quantities(self):
        reference_abs = np.dot(self.line_reference_vector, self.line_reference_vector)
        direction_abs = np.dot(self.line_direction_vector, self.line_direction_vector)
        cross_term = np.dot(self.line_reference_vector, self.line_direction_vector)
        return reference_abs, direction_abs, cross_term

    def get_position_parameters(self, reference_abs, direction_abs, cross_term):
        discriminant = math.sqrt(cross_term**2
                                 - reference_abs * direction_abs
                                 + direction_abs * self.global_problem.profit**2)
        position_parameter_plus = (-1*cross_term + discriminant) / direction_abs
        position_parameter_minus = (-1*cross_term - discriminant) / direction_abs
        return (position_parameter_plus, position_parameter_minus)

    def get_positions(self, position_parameters):
        position_parameter_plus, position_parameter_minus = position_parameters
        position_plus = self.line_reference_vector + position_parameter_plus * self.line_direction_vector
        position_minus = self.line_reference_vector + position_parameter_minus * self.line_direction_vector
        return position_plus, position_minus

    def set_partial_position(self, position_plus, position_minus):
        if np.all(position_plus > -0.00001):
            self.partial_position = position_plus
        elif np.all(position_minus > -0.00001):
            self.partial_position = position_minus
        else:
            raise Exception(f"Neither intersections with hypersphere are positive for dimension {self.dimension}")

    def output_all(self):
        self.output_basic_and_non_basic_variables()
        self.output_values()
        self.output_profit_information()
        self.output_vertex_position()

    def output_basic_and_non_basic_variables(self):
        basic_variables_string = [str(round(value, 2)) for value in self.basic_variables]
        non_basic_variables_string = [str(round(value, 2)) for value in self.non_basic_variables]
        print((f"Outputting basic and non basic variables for dimension {self.dimension}\n"
               f"Basic variables: {', '.join(basic_variables_string)}\n"
               f"Non-basic variables: {', '.join(non_basic_variables_string)}\n"))

    def output_values(self):
        print(f"Outputting values for dimension {self.dimension}")
        for basic_variable, value in zip(self.basic_variables, self.values):
            print(f"{basic_variable}: {round(value, 2)}")
        print("")

    def output_vertex_position(self):
        print(f"Outputting vertex position for dimension {self.dimension}")
        vertex_position = self.get_vertex_position()
        for index, value in enumerate(vertex_position):
            print(f"{index}: {value}")
        print("")

    def get_vertex_position(self):
        vertex_position = [self.get_spatial_variable_value(dimension)
                           for dimension in self.spatial_variables]
        vertex_position = np.array(vertex_position)
        return vertex_position
    
    def get_spatial_variable_value(self, spatial_variable):
        if spatial_variable in self.basic_variables:
            value = self.values[self.basic_variables == spatial_variable][0]
        else:
            value = 0
        return value

    def output_profit_information(self):
        print(f"Outputting profit information for dimension {self.dimension}")
        print(f"Profit: {self.profit}")
        for non_basic_variable, profit_coefficient in zip(self.non_basic_variables, self.profit_row):
            print(f"{non_basic_variable}: {profit_coefficient}")
        print("")

    def output_line_of_movement(self):
        print((f"Reference vector: {self.line_reference_vector}\n"
               f"Direction vector: {self.line_direction_vector}\n"
               f"Dimension: {self.dimension}\n"))

