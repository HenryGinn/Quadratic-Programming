import numpy as np

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
        self.initialise_tableau_from_input_data()
        self.pivot_column_index = None

    def initialise_tableau_from_input_data(self):
        self.set_dimensions()
        self.set_spatial_and_non_spatial_variables()
        self.initialise_basic_and_non_basic_variables()
        self.set_initial_tableau()

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

    def set_initial_tableau(self):
        self.values = np.copy(self.constraint_vector)
        self.set_initial_profit_data()
        self.tableau_body = np.concatenate((self.constraint_matrix, np.identity(self.slack_dimensions)), axis=1)
        self.tableau = np.concatenate((self.tableau_body, self.values.reshape(-1, 1)), axis=1)
        self.tableau = np.vstack((self.tableau, self.profit_row))

    def set_initial_profit_data(self):
        self.profit = 0
        self.profit_row = np.hstack((self.profit_vector, self.profit))

    def get_potential_profit(self):
        theta_column = self.get_theta_column()
        self.pivot_row_index = np.argmin(theta_column)
        potential_profit = self.process_theta_column(theta_column)
        return potential_profit

    def get_theta_column(self):
        pivot_column = self.tableau_body[:, self.pivot_column_index]
        valid_theta_array = self.get_valid_theta_array(pivot_column)
        theta_column = np.where(valid_theta_array, self.values/pivot_column, np.inf)
        self.debug_theta_computation(pivot_column, theta_column, valid_theta_array)
        return theta_column

    def get_valid_theta_array(self, pivot_column):
        pivot_column_sign = np.sign(np.around(pivot_column, 4)).astype('int')
        value_column_sign = np.sign(np.around(self.values, 4)).astype('int')
        valid_theta_array = self.valid_theta_signs[value_column_sign, pivot_column_sign]
        return valid_theta_array

    def debug_theta_computation(self, pivot_column, theta_column, valid_theta_array):
        if self.debug_theta:
            theta_computation_array = np.vstack((pivot_column,
                                                 self.values,
                                                 theta_column,
                                                 valid_theta_array))
            print("Debugging theta computation. Columns are pivot column, values, theta, and whether theta is valid")
            print(np.transpose(theta_computation_array))

    def process_theta_column(self, theta_column):
        if theta_column[self.pivot_row_index] == np.inf:
            potential_profit = -np.inf
        else:
            potential_profit = self.compute_potential_profit()
        return potential_profit

    def compute_potential_profit(self):
        pivot_value = self.tableau[self.pivot_column_index, self.pivot_row_index]
        profit_pivot_column = self.profit_row[self.pivot_column_index]
        value_pivot_row = self.values[self.pivot_row_index]
        profit_row_multiplier = profit_pivot_column/pivot_value
        potential_profit = self.profit - value_pivot_row*profit_row_multiplier
        return potential_profit

    def pivot(self):
        pass

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
        print(self)
        self.output_tableau()
        self.output_basic_and_non_basic_variables()
        self.output_values()
        self.output_profit_information()
        self.output_vertex_position()

    def output_basic_and_non_basic_variables(self):
        basic_variables_string = [str(round(value, 2)) for value in self.basic_variables]
        non_basic_variables_string = [str(round(value, 2)) for value in self.non_basic_variables]
        print(("Outputting basic and non basic variables\n"
               f"Basic variables: {', '.join(basic_variables_string)}\n"
               f"Non-basic variables: {', '.join(non_basic_variables_string)}\n"))

    def output_values(self):
        print("Outputting values")
        for basic_variable, value in zip(self.basic_variables, self.values):
            print(f"{basic_variable}: {round(value, 2)}")
        print("")

    def output_tableau(self):
        print(("Outputting tableau\n"
               f"{self.tableau}\n"))

    def output_vertex_position(self):
        print("Outputting vertex position")
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
            value = self.basic_variable[self.basic_variables == spatial_variable]
        else:
            value = 0
        return value

    def output_profit_information(self):
        print("Outputting profit information")
        print(f"Profit: {self.profit}")
        for non_basic_variable in self.non_basic_variables:
            print(f"{non_basic_variable}: {self.profit_vector[non_basic_variable]}")
        print("")
        
    def __str__(self):
        string = ((f"Dimension: {self.dimension}\n"
                   f"Pivot column: {self.pivot_column_index}\n"))
        return string
