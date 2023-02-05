import numpy as np
from copy import deepcopy
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
        self.set_initial_tableaux()
        self.solved_status = "Unsolved"

    def set_dimensions(self):
        self.space_dimensions = self.constraint_matrix.shape[1]
        self.slack_dimensions = self.constraint_matrix.shape[0]
        self.total_dimensions = self.space_dimensions + self.slack_dimensions

    def set_initial_tableaux(self):
        initial_tableau = self.get_initial_tableau()
        self.tableaux = [self.create_tableau_dimension(initial_tableau, dimension)
                         for dimension in range(self.space_dimensions)]

    def create_tableau_dimension(self, initial_tableau, dimension):
        tableau_dimension = deepcopy(initial_tableau)
        tableau_dimension.dimension = dimension
        tableau_dimension.pivot_column_index = dimension
        return tableau_dimension

    def get_initial_tableau(self):
        initial_profit_vector = self.get_initial_profit_vector()
        initial_tableau = Tableau(-1, self.constraint_matrix,
                                  self.constraint_vector,
                                  initial_profit_vector)
        return initial_tableau
        
    def get_initial_profit_vector(self):
        profit_function_space = -1*np.ones(self.space_dimensions)
        profit_function_slack = np.zeros(self.slack_dimensions)
        profit_vector = np.concatenate((profit_function_space,
                                        profit_function_slack), axis=0)
        return profit_vector

    def solve(self):
        while self.solved_status == "Unsolved":
            self.iterate()
            self.output_tableaux()
            input()

    def iterate(self):
        updating_dimension = self.get_updating_dimension()

    def get_updating_dimension(self):
        potential_profit_list = [tableau.get_potential_profit() for tableau in self.tableaux]
        print(potential_profit_list)

    def output_problem_constraints(self):
        print("Problem constraints")
        print(self.constraint_matrix)
        print(self.constraint_vector)
        print("")

    def output_tableaux(self):
        for tableau in self.tableaux:
            print("#################################################\n")
            tableau.output_all()

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
problem.solve()
