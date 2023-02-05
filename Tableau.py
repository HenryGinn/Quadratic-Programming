import numpy as np

class Tableau():

    """
    Constructs, manipulates, and outputs information about a simplex tableau.

    Constructs an initial tableau from data Ax <= b and profit function c^Tx.
    Computes pivot column, theta_column, pivot_row, and performs row operations
    Outputs basic and non-basic variables, profit, values, and the whole tableau
    """

    def __init__(self, constraint_matrix, constraint_vector, profit_vector):
        self.constraint_matrix = constraint_matrix
        self.constraint_vector = constraint_vector
        self.profit_vector = profit_vector
        self.set_dimensions()
        self.initialise_basic_and_non_basic_variables()
        self.set_initial_tableau()
        self.output_tableau()

    def set_dimensions(self):
        self.space_dimensions = self.constraint_matrix.shape[1]
        self.slack_dimensions = self.constraint_matrix.shape[0]
        self.total_dimensions = self.space_dimensions + self.slack_dimensions

    def initialise_basic_and_non_basic_variables(self):
        self.non_basic_variables = np.array(range(self.space_dimensions))
        self.basic_variables = np.array(range(self.space_dimensions, self.total_dimensions))

    def output_basic_and_non_basic_variables(self):
        print(("Outputting basic and non basic variables\n"
               f"Basic variables: {self.basic_variables}\n"
               f"Non-basic variables: {self.non_basic_variables}\n"))

    def set_initial_tableau(self):
        self.values = np.zeros(self.slack_dimensions).reshape(-1, 1)
        self.set_initial_profit_data()
        self.body = np.concatenate((self.constraint_matrix, np.identity(self.slack_dimensions)), axis=1)
        self.tableau = np.concatenate((self.body, self.values), axis=1)
        self.tableau = np.vstack((self.tableau, self.profit_row))

    def set_initial_profit_data(self):
        self.profit = 0
        self.profit_row = np.hstack((self.profit_vector, self.profit))

    def output_tableau(self):
        print(("Outputting tableau\n"
               f"{self.tableau}\n"))
