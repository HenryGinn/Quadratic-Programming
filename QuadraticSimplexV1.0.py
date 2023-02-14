import numpy as np
from copy import deepcopy
from Tableau import Tableau

class QuadraticSimplex():

    """ Each object is an optimisation problem to maximise the objective
    function x^Tx subject to constraints Ax<=b. All variables must be
    positive and the origin must be a feasible point.

    For more details on the algorithm, implementation, and formulation
    of quadratic problems into this form see the README document. """

    def __init__(self, constraint_matrix, constraint_vector):
        self.constraint_matrix = constraint_matrix
        self.constraint_vector = constraint_vector
        self.set_dimensions()
        self.set_initial_tableaux()
        self.set_space_constraints()
        self.solved_status = "Unsolved"
        
    def set_dimensions(self):
        self.space_dimensions = self.constraint_matrix.shape[1]
        self.slack_dimensions = self.constraint_matrix.shape[0]
        self.total_dimensions = self.space_dimensions + self.slack_dimensions

    def set_initial_tableaux(self):
        self.set_initial_profit_vector()
        initial_tableau = Tableau(self, -1, self.profit_vector)
        self.tableaux = [self.create_tableau_dimension(initial_tableau, dimension)
                         for dimension in range(self.space_dimensions)]
        
    def set_initial_profit_vector(self):
        profit_function_space = -1*np.ones(self.space_dimensions)
        profit_function_slack = np.zeros(self.slack_dimensions)
        self.profit_vector = np.concatenate((profit_function_space,
                                             profit_function_slack), axis=0)
        self.profit = 0

    def create_tableau_dimension(self, initial_tableau, dimension):
        tableau_dimension = deepcopy(initial_tableau)
        tableau_dimension.global_problem = self
        tableau_dimension.dimension = dimension
        tableau_dimension.pivot_column_index = dimension
        tableau_dimension.set_tableau_components()
        return tableau_dimension

    def set_space_constraints(self):
        non_negativity_constraints = np.identity(self.space_dimensions)
        self.space_constraints = np.concatenate((self.constraint_matrix,
                                                 non_negativity_constraints),
                                                axis=0)

    def solve(self):
        while self.solved_status == "Unsolved":
            print("#################### NEW ITERATION ####################\n")
            self.output_tableaux()
            print(f"Global profit vector: {-1*self.profit_vector}\n")
            self.iterate()
            input()

    def iterate(self):
        self.set_updating_tableau()
        print(f"Updating tableau: {self.updating_tableau.dimension}\n")
        self.updating_tableau.pivot()
        self.set_profit()
        self.compute_partial_positions()

    def set_updating_tableau(self):
        potential_profit_list = [tableau.get_potential_profit()
                                 for tableau in self.tableaux]
        updating_dimension = np.argmin(potential_profit_list)
        self.updating_tableau = self.tableaux[updating_dimension]

    def set_profit(self):
        self.updating_tableau.set_basic_variable_spatial_dict()
        dict_values = self.updating_tableau.basic_variable_spatial_dict.values()
        non_trivial_spatial_variables = np.array(list(dict_values))
        self.profit = sum(non_trivial_spatial_variables**2)

    def compute_partial_positions(self):
        for tableau in self.tableaux:
            if tableau != self.updating_tableau:
                tableau.get_line_of_movement()

    def output_problem_constraints(self):
        print("Problem constraints")
        print(self.constraint_matrix)
        print(self.constraint_vector)
        print("")

    def output_tableaux(self):
        for tableau in self.tableaux:
            print("#################### NEW DIMENSION ####################\n")
            tableau.output_all()

    def output_profit(self):
        print((f"Outputting global profit information\n"
               f"Profit: {self.profit}\n"
               f"Profit vector: {self.profit_vector}\n"))

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
#problem.output_tableaux()
problem.solve()
