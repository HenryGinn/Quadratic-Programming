import numpy as np
from Tableau import Tableau

class QuadraticSimplex():

    """
    Each object is an optimisation problem to maximise the objective function x^Tx subject to constraints Ax<=b. All variables must be positive and the origin must be a feasible point.

    For more details on the algorithm, implementation, and formulation of quadratic problems into this form see the README document.
    """

    def __init__(self, constraint_matrix, constraint_vector):
        self.constraint_matrix = constraint_matrix
        self.constraint_vector = constraint_vector
        self.set_dimensions()
        self.set_initial_tableau()

    def set_dimensions(self):
        self.space_dimensions = self.constraint_matrix.shape[1]
        self.slack_dimensions = self.constraint_matrix.shape[0]
        self.total_dimensions = self.space_dimensions + self.slack_dimensions

    def set_initial_tableau(self):
        initial_profit_vector = self.get_initial_profit_vector()
        self.initial_tableau = Tableau(0, self.constraint_matrix, self.constraint_vector, initial_profit_vector)
        self.initial_tableau.output_basic_and_non_basic_variables()
        self.initial_tableau.output_values()
        self.initial_tableau.output_tableau()

    def get_initial_profit_vector(self):
        profit_function_space = -1*np.ones(self.space_dimensions)
        profit_function_slack = np.zeros(self.slack_dimensions)
        profit_vector = np.concatenate((profit_function_space,
                                        profit_function_slack), axis=0)
        return profit_vector

    def output_problem_constraints(self):
        print("\nProblem constraints")
        print(self.constraint_matrix)
        print(self.constraint_vector)

    def __str__(self):
        string = (f"Space dimensions: {self.space_dimensions}\n"
                  f"Slack dimensions: {self.slack_dimensions}\n"
                  f"Total dimensions: {self.total_dimensions}\n")
        return string

constraint_matrix = np.array([[3, 2],
                              [-12, 13],
                              [1, -3],
                              [6, 5]])
constraint_vector = np.array([55, 13, 2, 120])

problem = QuadraticSimplex(constraint_matrix, constraint_vector)
