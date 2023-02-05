import numpy as np

class Tableau():

    """
    Constructs, manipulates, and outputs information about a simplex tableau.

    Constructs an initial tableau from data Ax <= b and profit function c^Tx.
    Computes pivot column, theta_column, pivot_row, and performs row operations
    Outputs basic and non-basic variables, profit, values, and the whole tableau
    """

    def __init__(self, dimension, constraint_matrix, constraint_vector, profit_vector):
        self.dimension = dimension
        self.constraint_matrix = constraint_matrix
        self.constraint_vector = constraint_vector
        self.profit_vector = profit_vector
        self.initialise_tableau_from_input_data()
        self.pivot_column = None

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

    def get_theta_min(self):
        print(self.values)
        print(self.tableau_body[:, self.pivot_column])
        return -1

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
        if spatial_variable in self.basic_variable_spatial_dict:
            value = self.basic_variable_spatial_dict[spatial_variable]
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
                   f"Pivot column: {self.pivot_column}\n"))
        return string
